import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch2(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 2", ch_num_style))
    story.append(p("LITERATURE REVIEW AND THEORETICAL FOUNDATIONS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("2.1 Evolution of Applicant Tracking Systems (ATS)", h1_style))
    story.append(p("Automated recruitment technology has evolved across three distinct technological paradigms. First-generation Applicant Tracking Systems, deployed widely in the late 1990s and early 2000s, functioned strictly as relational database repositories for digitized CVs. Filtering was performed via rigid SQL substring queries and boolean search expressions (e.g., 'Java AND Spring AND AWS'). These early systems were profoundly fragile: applicants who utilized semantic synonyms, hyphenated expressions, or graphical layouts were routinely omitted from search results."))
    story.append(p("Second-generation systems introduced statistical Natural Language Processing (NLP) techniques, employing Term Frequency-Inverse Document Frequency (TF-IDF) and Bag-of-Words (BoW) representations to score candidate-job similarity. While offering greater flexibility than binary boolean matching, second-generation parsers remained vulnerable to frequency gaming and keyword stuffing: candidates could inflate their ranking by packing unverified skill lists into white fonts or invisible footers. Third-generation systems incorporate transformer language models and deep contextual embeddings; however, as demonstrated across our empirical audits, commercial deployments frequently exhibit severe architectural fragmentation, isolating document screening from live technical evaluation and diagnostic feedback."))

    story.append(p("2.2 Information Extraction and Polysemous Token Collisions", h1_style))
    story.append(p("Information extraction from technical resumes presents unique linguistic challenges that confound general-purpose NLP tokenizers. Contemporary software engineering vocabularies feature single-letter programming languages ('C', 'R'), common English verbs ('Go', 'Rust'), framework designations ('Spring', 'Flutter'), and architectural concepts ('REST'). Off-the-shelf named entity recognition (NER) models and basic regex patterns produce massive false-positive collision rates when encountering conversational English prose (e.g., 'go to market strategy', 'in c-suite discussions', 'spring release', 'the rest of the platform') (Zhang et al., 2023). Resolving this requires context-guarded assertion shielding and structural boundary validation."))

    story.append(p("2.3 Temporal Experience Reasoning and Credential Ontologies", h1_style))
    story.append(p("A persistent flaw in existing resume parsers is the absence of formal temporal algebra. When candidates hold overlapping part-time positions, concurrent freelance consulting contracts, or simultaneous startup roles, naive subtraction sums each duration independently, artificially inflating commercial experience by 50% to 200%. Furthermore, legacy parsers fail to distinguish self-directed academic coursework projects from verified corporate employment, allowing novice graduates to claim senior engineering status based on academic hackathons."))
    story.append(p("Similarly, academic credential scoring in commercial tools frequently collapses educational attainment into a monolithic scalar score. This introduces severe qualification distortions: a candidate possessing an advanced Doctorate in English Literature often outscores an accredited Bachelor of Science in Computer Science when evaluated for a Senior Backend Engineering role. An authentic recruitment ontology must strictly decouple degree attainment tier levels from disciplinary field relevance."))

    story.append(p("2.4 Multi-Modal Autonomous Technical Examination", h1_style))
    story.append(p("Autonomous technical assessment has expanded beyond multiple-choice quizzes into conversational and coding evaluation. In technical interviews, evaluating candidate verbal clarity and domain depth requires high-fidelity speech-to-text (STT) transcription and semantic similarity matching. Deep transformer architectures, notably OpenAI's Whisper model, achieve word error rates (WER) below 10% across diverse accents, enabling robust voice transcription in multicultural hiring environments (Radford et al., 2023)."))
    story.append(p("To score open-ended descriptive responses against reference rubrics without requiring verbatim lexical matches, bi-encoder architectures like Sentence-BERT (SBERT) map answers into dense 768-dimensional vector spaces, computing cosine similarity that reflects authentic conceptual understanding (Reimers & Gurevych, 2019). Simultaneously, evaluating candidate programming proficiency requires safe execution sandboxes. Abstract Syntax Tree (AST) inspection and resource-capped process sandboxing provide essential safeguards against infinite loops, fork bombs, and malicious file system access during automated code verification."))

    story.append(p("2.5 Learning-to-Rank and Algorithmic Fairness in Personnel Selection", h1_style))
    story.append(p("Candidate ranking operates as an Information Retrieval (IR) optimization problem over high-dimensional applicant profiles. Learning-to-Rank (LTR) algorithms optimize ordering directly on listwise utility metrics such as Normalized Discounted Cumulative Gain (NDCG) and Mean Average Precision (MAP) (Burges et al., 2010). The LambdaMART algorithm, which combines Gradient Boosted Decision Trees with smoothed pairwise lambda-gradients, represents the state-of-the-art across information retrieval benchmarks (Ke et al., 2017)."))
    story.append(p("However, in high-stakes personnel selection, purely black-box ranking engines pose significant ethical and regulatory risks regarding algorithmic bias and disparate impact (Hardt et al., 2016; Zehlike et al., 2017). Legislative frameworks such as the European Union Artificial Intelligence Act (EU AI Act, Annex III) and New York City Local Law 144 mandate that automated employment decision tools (AEDTs) provide transparent mathematical explainability and undergo rigorous annual bias audits. Multi-Attribute Utility Theory (MAUT) provides a mathematically auditable, linear scoring baseline that can be paired with closed-form SHapley Additive exPlanations (SHAP) to guarantee full legal transparency (Lundberg & Lee, 2017)."))

    story.append(p("2.6 Skill Gap Modeling and Closed-Loop Career Mobility", h1_style))
    story.append(p("In conventional enterprise pipelines, talent rejection is treated as a terminal, non-actionable outcome. Transforming candidate assessment into predictive career development requires quantifying the semantic distance between applicant competencies and dynamic job requisition benchmarks (Zhang et al., 2023). Supervised tabular algorithms, particularly Gradient Boosted Decision Trees (GBDT), excel at modeling non-linear tabular interactions across candidate feature vectors (Friedman, 2001). Missing skills must then be sequenced into realistic, paced learning trajectories rather than overwhelmed inventories. Furthermore, modeling promotional and lateral transitions across a formal Directed Acyclic Graph (DAG) allows talent acquisition systems to navigate internal talent mobility and retain high-potential candidates across adjacent roles."))

    story.append(p("2.7 Forensic Audit of Synthetic Data Leakage in Academic Literature", h1_style))
    story.append(p("A critical methodological revelation of our research is the discovery of pervasive synthetic benchmark leakage in published recruitment NLP literature. Multiple contemporary studies in automated resume parsing and job role classification report artificial, near-perfect performance figures (Macro F1 = 1.0, Accuracy = 100%). Through forensic replication, we established that these published models were trained and tested on synthetic datasets generated from rigid template engines. Classifiers simply memorized invariant template boilerplates and target class headers. When evaluated on authentic real-world resumes, these models suffered total performance collapse. This underscores the imperative for evaluating on authentic, heterogeneous applicant resumes with strictly isolated feature vectorization."))

    story.append(p("2.8 Cross-Component Research Gap Synthesis", h1_style))
    story.append(p("Table 2.1 synthesizes the critical limitations identified across contemporary literature and establishes how the integrated RecruitAI ecosystem addresses each gap:"))

    lit_data = [
        [p("<b>Recruitment Domain</b>", body_style), p("<b>State-of-the-Art Limitations</b>", body_style), p("<b>RecruitAI Group Solution</b>", body_style), p("<b>Component Lead</b>", body_style)],
        [p("Resume Screening &amp; Entity Extraction", body_style), p("Brittle keyword matching; polysemous token collisions (C, Go, REST); synthetic leakage.", body_style), p("Context-guarded NER look-arounds; Lebesgue interval algebra; 2D credential decoupling; 4,000 real CV corpus.", body_style), p("C1: D. T. D. Perera<br/>(IT22089236)", body_style)],
        [p("Technical Interview Assessment", body_style), p("Static canned questions; isolated from resume screening; binary MCQ testing without verbal nuance.", body_style), p("Adaptive RAIGS question retrieval (18.7k Q-bank); Whisper voice STT; SBERT rubric grading; AST sandbox.", body_style), p("C2: Dulnith K. D.<br/>(IT22094872)", body_style)],
        [p("Candidate Ranking &amp; Decision Support", body_style), p("Opaque black-box models; ad-hoc spreadsheet heuristics; lack of disparate impact audits.", body_style), p("Linear CSS with soft prerequisite gating; LambdaMART comparator; demographic parity audit (Delta_DP=0.008).", body_style), p("C3: K. G. Savinda N. Perera<br/>(IT22027610)", body_style)],
        [p("Skill Gap &amp; Career Development", body_style), p("Terminal rejection dead-ends; uninformative rejection notices; unranked laundry-list skills.", body_style), p("Fuzzy/semantic gap analysis; 67-feature GBDT hireability model; paced roadmap (2 skills/mo); DAG career lattice.", body_style), p("C4: Yenura S. Karunanayaka<br/>(IT22306272)", body_style)]
    ]
    lit_table = Table(lit_data, colWidths=[95, 140, 160, 92])
    lit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(lit_table)
    story.append(p("Table 2.1: Synthesis of Academic Research Gaps across Enterprise Recruitment and RecruitAI Ecosystem Solutions.", caption_style))
    story.append(PageBreak())
