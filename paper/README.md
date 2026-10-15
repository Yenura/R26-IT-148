# IEEE Conference Paper: Fair and Explainable Candidate Ranking with Skill-Gap Guided Career Development

**Authors:**  
- **Y.S. Karunanayaka** (`it22306272@my.sliit.lk`)  
- **Perera K.G.S.N.** (`it22027610@my.sliit.lk`)  
- **Perera D.T.D.** (`it22089236@my.sliit.lk`)  
*Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka*

---

## 📁 Directory Files

- **`main.tex`**: The primary LaTeX source file formatted using the official IEEE conference standard (`IEEEtran.cls`).
- **`references.bib`**: BibTeX bibliography database containing all 5 cited works.
- **`IEEEtran.cls`**: Official IEEE document class file (v1.8b, 281 KB) included locally for 100% standalone, offline compilation.

---

## 🚀 How to Compile

### Option 1: Overleaf (Recommended)
1. Zip the contents of this `paper/` folder (`main.tex`, `references.bib`, and `IEEEtran.cls`).
2. Log into [Overleaf](https://www.overleaf.com), click **New Project** $\rightarrow$ **Upload Project**, and select the zip file.
3. Select `pdfLaTeX` as the compiler and click **Recompile**.

### Option 2: Local Compilation (Command Line)
If you have TeX Live / MiKTeX installed:
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Option 3: VS Code / TeXstudio
Open `paper/main.tex` directly in VS Code with the **LaTeX Workshop** extension, or in **TeXstudio**, and click **Build / View**.

---

## 📄 Key Sections & Formulations Included

1. **Title & SLIIT Affiliations**: Configured with proper 3-column author block.
2. **Mathematical Formulations**:
   - Equation (1): $S_{cv} = w_{edu}S_{edu} + w_{exp}S_{exp} + w_{skill}S_{skill}$
   - Equation (2): $S_{int} = w_{mcq}P_{mcq} + w_{desc}P_{desc} + w_{code}P_{code}$, $CSS = 0.40S_{cv} + 0.60S_{int}$
   - Equation (3): $CSS = \phi_0 + \sum \phi_i$ (Exact linear SHAP formulation)
3. **Table I: Ablation Study (All 20 Roles)**:
   - Formatted with booktabs rules (`\toprule`, `\midrule`, `\bottomrule`) comparing single-source models, AHP/TOPSIS, CSS Proposed, and LambdaMART.
4. **References**: Formatted with both inline `thebibliography` (self-contained) and external `references.bib` for maximum compatibility.
