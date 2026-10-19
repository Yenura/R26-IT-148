# T5 question-generation — evaluation report

- model: `models\t5_qg`  (12,161,536 params)
- eval set: first 400 of 556 `qg_dataset_v2.json` validation rows
- generation: greedy (num_beams=1), max_new_tokens=128, prompt truncated to 64 tokens
- metrics: corpus BLEU-4 (clipped 1-4 gram + brevity penalty), ROUGE-L F1 (LCS), field-validity vs the app's parser, exact-match

## Overall

| metric | value |
|---|---|
| BLEU-4 | 10.93 |
| ROUGE-L F1 | 21.53 |
| field-valid % | 61.25 |
| exact-match % | 0.0 |
| n | 400 |

## By question type

| type | n | BLEU-4 | ROUGE-L | field-valid % |
|---|---|---|---|---|
| [Coding] | 122 | 0.42 | 6.53 | 0.0 |
| [Descriptive] | 39 | 4.84 | 17.8 | 100.0 |
| [MCQ] | 239 | 16.0 | 29.8 | 86.19 |

- implied all-pass rate for a 2 MCQ + 1 descriptive + 1 coding batch: ~0.0% (upper bound - the real gate, `_is_good_question`, is stricter)

## Training progression (generation metrics, not teacher-forced)

- untrained baseline: ROUGE-L 0.0 / BLEU-4 0.0 / field-valid 0.0%

| step | phase | ROUGE-L | BLEU-4 | field-valid % | exact % |
|---|---|---|---|---|---|
| 0 | baseline | 0.0 | 0.0 | 0.0 | - |
| 150 | train | 0.0 | 0.0 | 0.0 | - |
| 300 | train | 10.41 | 2.8 | 0.0 | - |
| 450 | train | 9.5 | 3.24 | 29.7 | - |
| 600 | train | 8.2 | 3.07 | 18.8 | - |
| 750 | train | 10.24 | 3.53 | 14.1 | - |
| 900 | train | 9.98 | 4.13 | 0.0 | - |
| 1050 | train | 7.5 | 1.72 | 0.0 | - |
| 1200 | train | 9.76 | 3.72 | 26.6 | - |
| 1350 | train | 8.54 | 2.71 | 12.5 | - |
| 1500 | train | 9.73 | 3.19 | 32.8 | - |
| 1650 | train | 10.83 | 4.39 | 45.3 | - |
| 1800 | train | 10.91 | 4.68 | 40.62 | 0.0 |
| 2000 | train | 9.78 | 3.4 | 33.33 | 0.0 |
| 2200 | train | 13.46 | 5.58 | 47.92 | 0.0 |
| 2400 | train | 12.57 | 4.68 | 39.58 | 0.0 |
| 2600 | train | 15.47 | 6.24 | 60.42 | 0.0 |
| 2800 | train | 15.26 | 6.69 | 57.29 | 0.0 |
| 3000 | train | 15.48 | 7.06 | 57.29 | 0.0 |
| 3200 | train | 15.17 | 7.18 | 50.0 | 0.0 |
| 3400 | train | 15.31 | 7.59 | 54.17 | 0.0 |
| 3600 | train | 19.13 | 8.31 | 58.33 | 0.0 |
| 3800 | train | 17.35 | 8.46 | 59.38 | 0.0 |
| 4000 | train | 17.26 | 8.91 | 54.17 | 0.0 |
| 4200 | train | 17.82 | 8.63 | 57.29 | 0.0 |
| 4400 | train | 17.7 | 7.69 | 61.46 | 0.0 |
| 4600 | train | 18.07 | 8.81 | 55.21 | 0.0 |
| 4800 | train | 16.8 | 8.06 | 55.21 | 0.0 |
| 5000 | train | 16.99 | 8.03 | 53.12 | 0.0 |

- best checkpoint: step 4400 (ROUGE-L 17.7)
- training wall-clock: 153.4 min

## Spot-checks (prompt / reference / generated)

### [MCQ]

- **prompt**: `[MCQ] Backend Developer | scalability patterns | Easy`
  - reference: Q: What distinguishes a correct implementation of scalability patterns from a flawed one? / O: Focusing on middleware architecture while overlooking the actual requirements of scalability patterns. | Treating scalability p
  - generated: Q: Which of the following would a senior s? O: A superficial application of s that overlooks important edge cases. | An outdated approach to s current best practices. | A structured approach that directly satisfies the i
- **prompt**: `[MCQ] Frontend Developer | CSS layout systems (flexbox/grid) | Medium`
  - reference: Q: What is the main benefit of using CSS layout systems (flexbox/grid) in a Frontend Developer context? / O: Confusing CSS layout systems (flexbox/grid) with frontend build tools, which actually serves a different purpose.
  - generated: Q: Which of the following would a senior Blockchain Developer flag as a risk when CSS CSS pre pre pre pre preprocessors is handled incorrectly? O: A superficial application of CSS preprocessors that overlooks important e
- **prompt**: `[MCQ] Cybersecurity Analyst | security auditing | Medium`
  - reference: Q: Which of the following is NOT typically associated with security auditing? / O: An accurate, practical description of how security auditing functions in real Cybersecurity Analyst work. | Confusing security auditing wit
  - generated: Q: Which of the following would a senior Cybersecurity Analyst flag as a risk when security incident response process is handled incorrectly? O: A superficial application of security that overlooks important edge cases. 

### [Descriptive]

- **prompt**: `[Descriptive] Software Engineer | Java | Medium`
  - reference: Q: What is an array in Java, and how is it used to store multiple values of the same data type? / A: An array in Java is a data structure that stores a fixed-size collection of elements of the same data type. Arrays provid
  - generated: Q: What is the purpose of the ' class in Java? A: The ' class in Java is used to the ' class in Java is used to the a class in Java is used to the a class in Java is used to the a class in Java is used to the a class in 
- **prompt**: `[Descriptive] Software Engineer | Java | Easy`
  - reference: Q: What is the difference between a 'StringBuilder' and a 'StringBuffer' in Java? / A: Both 'StringBuilder' and 'StringBuffer' are mutable string classes in Java, but 'StringBuffer' is thread-safe (synchronized), while 'St
  - generated: Q: What is the purpose of the ' class in Java? A: The ' class in Java is used to the ' class in Java is used to the a class in Java is used to the a class in Java is used to the a class in Java is used to the a class in 
- **prompt**: `[Descriptive] Software Engineer | Java | Medium`
  - reference: Q: You are tasked with migrating an existing monolithic application to a microservices architecture. What factors would you consider when planning and executing the migration? / A: When planning and executing the migration
  - generated: Q: What is the purpose of the ' class in Java? A: The ' class in Java is used to the ' class in Java is used to the a class in Java is used to the a class in Java is used to the a class in Java is used to the a class in 

### [Coding]

- **prompt**: `[Coding] Software Engineer | String | Easy`
  - reference: Q: Length of Last Word. Given a string `s` consists of some words separated by spaces, return the length of the last word in the string. If the last word does not exist, return `0`. A word is a maximal substring consisti
  - generated: Q: a string n, return the n. You may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may may
- **prompt**: `[Coding] Software Engineer | Math | Medium`
  - reference: Q: Spiral Matrix III. On a 2 dimensional grid with `R` rows and `C` columns, we start at `(r0, c0)` facing east. Here, the north-west corner of the grid is at the first row and column, and the south-east corner of the gr
  - generated: Q: a string nn, return the nnnnnnnnn and . You are , , , , and . You are n, , , , and , and , and , and . You are , , and , and , and , and , and , and , and , and ,
- **prompt**: `[Coding] Software Engineer | Tree, Depth-first Search, Recursion | Hard`
  - reference: Q: Binary Tree Maximum Path Sum. A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence at most once. Note tha
  - generated: Q: Find the a string nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn and  and  and  and  and  and  and 

## App-path probes (real backend QuestionGenerator)

| role | type | role skill named | question |
|---|---|---|---|
| Software Engineer | MCQ | - | Which of the following best describes a senior Data Engineer flag as a risk when network security fundamentals is handled incorrectly? |
| Software Engineer | MCQ | - | Which of the following best describes network design? |
| Software Engineer | Descriptive | Java | What is the purpose of the ' keyword in Java? |
| Data Scientist | MCQ | - | Which of the following would a senior Data Scientist flag as a risk when data pipelines is handled incorrectly? |
| Data Scientist | MCQ | - | Which of the following would a senior Data Engineer flag as a risk when model architectures is handled incorrectly? |
| Data Scientist | Descriptive | - | What is the purpose of the ' in Java? |
| Cybersecurity Analyst | MCQ | Cybersecurity | Which of the following would a senior Cybersecurity Analyst flag as a risk when security incident response process is handled incorrectly? |
| Cybersecurity Analyst | MCQ | - | Which of the following best describes security incident triage? |
| Cybersecurity Analyst | Descriptive | - | What is the purpose of the ' keyword in Java? |
| Business/Systems Analyst | MCQ | - | Which of the following would a senior Business/Systems Analyst flag as a risk when requirements gathering techniques is handled incorrectly? |
| Business/Systems Analyst | MCQ | Documentation | Which of the following would a senior Business/Systems Analyst flag as a risk when business rules documentation is handled incorrectly? |
| Business/Systems Analyst | Descriptive | - | What is the purpose of the ' in Java? |

## Why the previous checkpoint was unusable

- `D:\GitHub\R26-IT-148\component2\models\_t5_qg_dead_checkpoint`: AutoTokenizer/from_pretrained FAILED: AttributeError: 'list' object has no attribute 'keys'
- its `tokenizer_config.json` had `extra_special_tokens` as a *list* (transformers 5.15.1 format); transformers 4.57.6 expects a dict, so `AutoTokenizer.from_pretrained` raised `AttributeError: 'list' object has no attribute 'keys'`.
- the saved weights were trained under that mismatch, so even forcing the tokenizer load produced degenerate output.
