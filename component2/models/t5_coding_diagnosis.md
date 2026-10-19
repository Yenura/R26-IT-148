# Why Coding collapses in the T5 QG model

Diagnosis for the question-generation model (`models/t5_qg`, 12.16M params,
trained from scratch on `models/qg_dataset_v2.json`).

Reproduce:

```powershell
cd component2
python ml/diagnose_coding_targets.py --data models/qg_dataset_v2.json --split train --tokenizer models/t5_qg
python ml/diagnose_coding_targets.py --data models/qg_dataset_v2.json --split val   --tokenizer models/t5_qg
```

Limits default to the training config (`ml/train_t5_qg_v2.py`): `max_src=64`,
`max_tgt=128`.

## Measured (tokenizer `models/t5_qg`, unk_id = 2)

Train split (n = 4996):

| type        | rows | share | target tokens p50 / p90 / max | truncated @128 | `<unk>` rate | rows w/ unk |
|-------------|-----:|------:|------------------------------:|---------------:|-------------:|------------:|
| mcq         | 2846 |  57%  | 101 / 118 / 180               | 3.5%           | 0.00%        | 1 / 2846    |
| coding      | 1668 |  33%  | **211 / 272 / 1229**          | **89.2%**      | **9.47%**    | **1668 / 1668** |
| descriptive |  482 |  10%  | 80 / 171 / 227                | 23.4%          | 0.00%        | 2 / 482     |

Val split (n = 556) is the same shape: coding p50 = 209, truncated 83.1%,
`<unk>` 9.11% on every coding row; mcq/descriptive `<unk>` ≈ 0%.

Characters that tokenize to `<unk>` (offsets mapped back to source):

| lost text | occurrences (sampled) |
|-----------|----------------------:|
| `` ` `` backtick   | 1555 |
| `\` backslash      | 1056 |
| `{`                | 642  |
| `}`                | 642  |
| `<`                | 49   |

## Reading

Three candidate causes were checked. Two are real, one is not:

1. **Truncation — dominant (89% of coding targets).** Median coding target is
   **211 tokens** against a **128-token** cap. Even the "good" half loses its
   tail, and the tail is exactly the part the field-validity check looks at
   (constraints, examples, test cases, answer). A truncated coding target can
   essentially never be field-valid → 0%.
2. **Tokenizer coverage — real but secondary.** The stock flan-t5 SentencePiece
   vocab (32k) has **no backtick, backslash, `{`, `}` or `<`** — every coding
   row contains at least one `<unk>`, so the exact characters code is made of
   are destroyed before training even starts.
3. **Row count — ruled out.** Coding is **33%** of the training set, not
   under-represented. Oversampling was not the issue.

So the order of blame is truncation ≫ tokenizer coverage ≫ (nothing else).

## Fixes (ordered by impact)

- **Shrink coding targets or raise `max_tgt`.** Coding needs ≈ 272 tokens at
  p90. Keeping the problem statement + constraints and sourcing examples/tests
  from the bank would fit under 128 without a longer model.
- **Code-safe tokenizer.** Train a compact ByteLevel BPE vocab (~8k) over the
  domain corpus that keeps `` ` ``, `\`, `{`, `}`, `<`, and real newlines —
  `ml/build_qg_tokenizer.py` — then pass `--tokenizer-dir` to
  `ml/train_t5_qg_v2.py`.
- **Escaping a fallback** without a new vocab: `{ → <LB>`, `} → <RB>`,
  `` ` → <BT> ``, `\ → <BS>` via `tokenizer.add_tokens`.

## The same audit, applied to Descriptive

Descriptive is field-valid but not *usable*: the model's Descriptive output is
also rejected wholesale, for a different reason — the training data is
role-homogeneous.

- `models/qg_dataset_v2.json` Descriptive: **482/482 rows are "Software
  Engineer"**, 251 of them named **Java**; every prompt is
  `[Descriptive] Software Engineer | Java | Medium`. Val is the same (50/50).
- The model faithfully memorizes that template and emits
  `"What is the purpose of the ' in Java?"` for *every* role, dropping the
  quoted identifier (a bare `\s'\s` that the gate rejects).
- 0/482 corpus targets contain a bare quote — the collapse happens at inference.

So Descriptive needs **role diversification of the corpus** before it can
serve; the gate is doing the right thing by keeping it on the bank meanwhile.

### Gate false-positive fixed alongside

Auditing `_is_good_question` surfaced a real bug: degeneracy was checked on the
**concatenation** of the MCQ options, so the standard distractors
`"All of the above"` and `"None of the above"` collided on the 3-gram
`"of the above"` and a perfectly good, on-topic MCQ was rejected. Options are
now checked **individually** (a real loop still shows up inside one option,
e.g. `"CSS CSS CSS preprocessors"`).

Effect on the live model, 20 roles (`backend/tests/qg_path_report.py`):

| metric                          | before | after |
|---------------------------------|-------:|------:|
| per-question gate pass rate     |  29%   | **42%** |
| roles serving ≥1 model question | 0 / 20 | **18 / 20** |
| served questions from the model  | 12%    | **16%** |

Remaining rejections are genuine: 12 descriptive bare-quote (the Java
template), 8 MCQ off-role, 2 MCQ repetition loops. Because failures are
dominated by broken text rather than word-form mismatches, the optional
relevance **lemmatization is not worth it** here.

## Action taken now

Rather than block on a retrain, **Coding is routed to the curated question
bank** and the model serves **MCQ + Descriptive only**, with a **per-question
gate** (`services/qg_engine.py`): every surviving question is served and each
rejected/absent slot is filled from the bank, so the model is used where it
works without ever serving filler or an unexecutable coding question. The
tokenizer/truncation fix above is the documented path to making the model serve
Coding too.
