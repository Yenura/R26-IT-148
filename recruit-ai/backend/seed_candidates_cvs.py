"""Seed script to register 10 top IT candidates, upload realistic structured CVs, and link them to the platform."""
import os
import sys
from datetime import datetime, timezone
import bcrypt
from bson import ObjectId
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR")
DB_NAME = os.getenv("DB_NAME", "HR")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

CANDIDATES_DATA = [
    {
        "full_name": "Alex Chen",
        "email": "alex.chen@gmail.com",
        "password": "Password123!",
        "phone": "+1 (415) 555-0182",
        "address": "San Francisco, CA, USA",
        "linkedin": "https://linkedin.com/in/alexchen-fullstack",
        "github": "https://github.com/alexchen-dev",
        "education": "B.Sc. in Computer Science - Stanford University (2020)",
        "experience_years": 5.0,
        "filename": "Alex_Chen_FullStack_Resume.pdf",
        "skills": [
            "React", "Node.js", "TypeScript", "PostgreSQL", "Docker", "Git",
            "AWS", "Python", "REST APIs", "GraphQL", "MongoDB", "Kubernetes", "Redis"
        ],
        "frameworks": ["React", "Express.js", "FastAPI", "Next.js", "Tailwind CSS"],
        "tools": ["Docker", "Kubernetes", "Git", "Postman", "AWS ECS", "Webpack", "Vite"],
        "languages": ["JavaScript", "TypeScript", "Python", "SQL", "HTML/CSS"],
        "certifications": ["AWS Certified Solutions Architect - Associate", "Meta Certified Full-Stack Developer"],
        "projects": [
            "Enterprise Microservices Portal: Architected React/TypeScript frontend and Node.js/PostgreSQL microservices handling 2M+ daily requests.",
            "Real-Time Collaboration Workspace: Built real-time canvas with WebSockets, Redis pub/sub, and optimistic UI updates.",
            "Cloud Infrastructure Automation: Configured Docker containers and AWS ECS pipelines reducing build times by 40%."
        ],
        "academic_projects": [
            "Distributed Key-Value Store: Implemented Raft consensus in Python with data replication across 5 simulated nodes.",
            "Scalable Web Crawler: Developed multi-threaded Python web indexing engine with Bloom filters."
        ],
        "personal_projects": [
            "OpenSource DevTools UI: Created open-source React component library with 1.2k GitHub stars.",
            "Full-Stack Job Tracker: SaaS dashboard built with Next.js, Prisma, and PostgreSQL."
        ],
        "project_experience_years": 5.0,
        "raw_text": """ALEX CHEN
San Francisco, CA | alex.chen@gmail.com | +1 (415) 555-0182
LinkedIn: linkedin.com/in/alexchen-fullstack | GitHub: github.com/alexchen-dev

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with 5 years of experience architecting resilient cloud web applications, high-performance REST and GraphQL APIs, and modern React/TypeScript frontends. Adept with Docker, PostgreSQL, Node.js, and AWS microservice environments.

CORE SKILLS & TECHNOLOGIES
- Languages: JavaScript (ES6+), TypeScript, Python, SQL, HTML5, CSS3
- Frontend: React, Redux Toolkit, Next.js, Tailwind CSS, Webpack, Vite
- Backend: Node.js, Express.js, FastAPI, REST APIs, GraphQL, gRPC
- Databases: PostgreSQL, MongoDB, Redis, MySQL
- Cloud & DevOps: AWS (ECS, S3, RDS, Lambda), Docker, Kubernetes, CI/CD, Git

PROFESSIONAL EXPERIENCE
Senior Full Stack Developer | Apex Cloud Systems (2022 - Present)
- Architected enterprise React/TypeScript dashboards and Node.js microservices serving 2M+ daily active requests with 99.98% uptime.
- Transitioned legacy monolithic backend to modular Dockerized microservices deployed on AWS ECS.
- Designed optimized PostgreSQL schemas and implemented Redis caching layers, cutting 95th percentile query latency by 45%.
- Mentored junior engineers, led code reviews, and championed unit/integration testing with Jest and Cypress.

Full Stack Software Engineer | Horizon Web Labs (2020 - 2022)
- Built interactive customer billing portals using React, TypeScript, and Tailwind CSS.
- Developed scalable RESTful backend services using Node.js, Express, and PostgreSQL.
- Automated continuous integration and deployment pipelines using GitHub Actions and Docker.

EDUCATION
B.Sc. in Computer Science | Stanford University (2016 - 2020)
- GPA: 3.85 / 4.0. Focus in Distributed Systems and Human-Computer Interaction.

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate
- Meta Certified Full-Stack Developer"""
    },
    {
        "full_name": "Sophia Rodriguez",
        "email": "sophia.rodriguez@gmail.com",
        "password": "Password123!",
        "phone": "+1 (408) 555-0149",
        "address": "Sunnyvale, CA, USA",
        "linkedin": "https://linkedin.com/in/sophiarodriguez-ai",
        "github": "https://github.com/sophia-ml",
        "education": "M.Sc. in Artificial Intelligence - Carnegie Mellon University (2021)",
        "experience_years": 4.5,
        "filename": "Sophia_Rodriguez_ML_AI_Resume.pdf",
        "skills": [
            "Python", "PyTorch", "TensorFlow", "MLOps", "Deep Learning", "NLP",
            "Transformers", "HuggingFace", "LLMs", "Docker", "Pandas", "SQL", "Scikit-Learn"
        ],
        "frameworks": ["PyTorch", "TensorFlow", "HuggingFace Transformers", "vLLM", "LangChain", "FastAPI"],
        "tools": ["Docker", "MLflow", "Weights & Biases", "Triton Inference Server", "CUDA", "Kubernetes"],
        "languages": ["Python", "C++", "SQL", "R"],
        "certifications": ["TensorFlow Developer Certificate", "AWS Certified Machine Learning - Specialty"],
        "projects": [
            "Enterprise LLM Fine-Tuning & RAG: Fine-tuned Llama-3 and Mistral models using LoRA/QLoRA on proprietary legal datasets.",
            "Real-Time Multimodal Classification: Productionized low-latency vision-language model inference on NVIDIA Triton serving 500 QPS.",
            "MLOps Automated Training Pipeline: Built continuous model retraining and evaluation workflows using MLflow and Docker."
        ],
        "academic_projects": [
            "Neural Audio Source Separation: Research paper published at NeurIPS workshop on transformer-based waveform decomposition.",
            "Cross-Lingual Semantic Retrieval: Evaluated multilingual transformer embeddings for zero-shot query matching."
        ],
        "personal_projects": [
            "OpenRAG Agent: Open-source local vector retrieval framework with 800+ stars.",
            "GPU Benchmark Suite: Python benchmarking harness measuring memory throughput across transformer attention layers."
        ],
        "project_experience_years": 4.5,
        "raw_text": """SOPHIA RODRIGUEZ
Sunnyvale, CA | sophia.rodriguez@gmail.com | +1 (408) 555-0149
LinkedIn: linkedin.com/in/sophiarodriguez-ai | GitHub: github.com/sophia-ml

PROFESSIONAL SUMMARY
Machine Learning & AI Research Engineer with 4.5 years of expertise designing, training, and deploying large-scale neural architectures, Transformer models, and real-time MLOps inference pipelines. Proven track record in NLP, LLM fine-tuning, and PyTorch acceleration.

TECHNICAL SKILLS
- Deep Learning & NLP: PyTorch, TensorFlow, Transformers, HuggingFace, LLMs, LoRA, RLHF, spaCy
- Machine Learning & Math: Scikit-Learn, Pandas, NumPy, SciPy, Statistical Modeling, Vector Embeddings
- MLOps & Production: Docker, Triton Inference Server, MLflow, Weights & Biases, vLLM, FastAPI, Kubernetes
- Languages: Python, C++, SQL, R

PROFESSIONAL EXPERIENCE
Senior Machine Learning Engineer | NeuralScale AI (2022 - Present)
- Spearheaded fine-tuning of frontier open-source LLMs (Llama-3, Mistral) using QLoRA and DPO for enterprise domain applications.
- Deployed low-latency inference pipelines on NVIDIA GPU clusters with vLLM and TensorRT, reducing latency by 55% at 500 QPS.
- Built automated model evaluation benchmarks and data curation pipelines filtering billions of training tokens.

Machine Learning Engineer | Cognitive Analytics (2021 - 2022)
- Trained transformer-based semantic search and entity extraction models using PyTorch and HuggingFace.
- Built automated MLOps pipelines on Docker and MLflow for experiment tracking, model registry, and containerized deployment.
- Collaborated with software engineering to integrate Python ML inference APIs into production applications.

EDUCATION
M.Sc. in Artificial Intelligence | Carnegie Mellon University (2019 - 2021)
B.Sc. in Computer Science & Applied Mathematics | UC San Diego (2015 - 2019)

CERTIFICATIONS
- AWS Certified Machine Learning - Specialty
- TensorFlow Certified Developer"""
    },
    {
        "full_name": "Marcus Johnson",
        "email": "marcus.johnson@gmail.com",
        "password": "Password123!",
        "phone": "+1 (512) 555-0177",
        "address": "Austin, TX, USA",
        "linkedin": "https://linkedin.com/in/marcusjohnson-devops",
        "github": "https://github.com/marcus-infra",
        "education": "B.Eng. in Software Systems - Georgia Tech (2019)",
        "experience_years": 5.0,
        "filename": "Marcus_Johnson_DevOps_SRE_Resume.pdf",
        "skills": [
            "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux",
            "Prometheus", "Python", "Go", "Azure", "Incident Management", "Git", "Ansible"
        ],
        "frameworks": ["Terraform", "Ansible", "Helm", "ArgoCD", "GitHub Actions"],
        "tools": ["Kubernetes", "Docker", "Prometheus", "Grafana", "Vault", "Linux", "AWS", "Azure"],
        "languages": ["Python", "Go", "Bash/Shell", "HCL", "YAML"],
        "certifications": ["Certified Kubernetes Administrator (CKA)", "HashiCorp Certified: Terraform Associate", "AWS Certified DevOps Engineer - Professional"],
        "projects": [
            "Multi-Region Kubernetes Fleet: Engineered automated multi-cluster deployment topology across 3 AWS regions using Terraform and Helm.",
            "GitOps Continuous Delivery: Implemented ArgoCD and GitHub Actions pipelines achieving 100+ zero-downtime production deployments daily.",
            "Unified Observability Platform: Built Prometheus, Thanos, and Grafana telemetry monitoring 10,000+ container metrics in real time."
        ],
        "academic_projects": [
            "Automated Cloud Failover Simulator: Simulated network partition chaos tests across geo-distributed Linux nodes.",
            "Secure Container Sandbox: Built lightweight Linux namespace isolation daemon in Go."
        ],
        "personal_projects": [
            "Terraform AWS Baseline Modules: Open source Terraform registry modules with 40k+ downloads.",
            "K8s Resource Optimizer: Go CLI utility auditing pod CPU/Memory requests vs actual metrics."
        ],
        "project_experience_years": 5.0,
        "raw_text": """MARCUS JOHNSON
Austin, TX | marcus.johnson@gmail.com | +1 (512) 555-0177
LinkedIn: linkedin.com/in/marcusjohnson-devops | GitHub: github.com/marcus-infra

PROFESSIONAL SUMMARY
DevOps & Site Reliability Engineer with 5 years of expertise orchestrating containerized infrastructure, automated CI/CD release pipelines, Infrastructure-as-Code (Terraform), and high-availability Kubernetes clusters across AWS and Azure cloud platforms.

TECHNICAL SKILLS
- Cloud Platforms: AWS (EKS, VPC, IAM, RDS, Route53), Microsoft Azure, GCP
- Container Orchestration: Kubernetes, Docker, Helm, ArgoCD, containerd
- Infrastructure as Code & Automation: Terraform, Ansible, CloudFormation, Packer
- Monitoring & Telemetry: Prometheus, Grafana, Thanos, Datadog, ELK Stack, OpenTelemetry
- Languages & Scripting: Python, Go, Bash/Shell Scripting, Linux Kernel Administration

PROFESSIONAL EXPERIENCE
Lead DevOps & SRE Engineer | CloudCore Systems (2022 - Present)
- Managed 15+ multi-region production Kubernetes (EKS) clusters supporting 200+ microservices with 99.99% availability.
- Standardized Terraform modules across 12 engineering teams, enforcing security guardrails and IAM least-privilege policies.
- Built GitOps delivery pipelines with ArgoCD and GitHub Actions, reducing deployment rollout failure rate from 8% to under 0.2%.
- Established on-call incident response runbooks, automated chaos testing drills, and SLO alerting in Prometheus and Grafana.

DevOps Infrastructure Engineer | DataStream Tech (2019 - 2022)
- Automated containerization and cloud migrations for 40+ legacy services into Docker and Kubernetes.
- Maintained centralized ELK log aggregators and Prometheus monitoring systems processing 5TB+ daily telemetry logs.
- Developed custom Go and Python CLI tools to automate ephemeral development environment provisioning.

EDUCATION
B.Eng. in Software Systems & Computer Engineering | Georgia Institute of Technology (2015 - 2019)

CERTIFICATIONS
- Certified Kubernetes Administrator (CKA)
- AWS Certified DevOps Engineer - Professional
- HashiCorp Certified: Terraform Associate"""
    },
    {
        "full_name": "Elena Rostova",
        "email": "elena.rostova@gmail.com",
        "password": "Password123!",
        "phone": "+1 (703) 555-0134",
        "address": "Reston, VA, USA",
        "linkedin": "https://linkedin.com/in/elenarostova-security",
        "github": "https://github.com/elena-cybersec",
        "education": "B.Sc. in Cybersecurity & Information Assurance - Purdue University (2020)",
        "experience_years": 4.0,
        "filename": "Elena_Rostova_Cybersecurity_Resume.pdf",
        "skills": [
            "Network Security", "SIEM", "Firewalls", "Threat Analysis", "Linux",
            "Python", "Incident Response", "Wireshark", "Cryptography", "Ethical Hacking", "Git"
        ],
        "frameworks": ["MITRE ATT&CK", "NIST CSF", "ISO 27001", "OWASP Top 10"],
        "tools": ["Splunk", "Microsoft Sentinel", "Wireshark", "Burp Suite", "Snort", "Suricata", "CrowdStrike Falcon", "Nmap"],
        "languages": ["Python", "Bash", "SQL", "PowerShell"],
        "certifications": ["Certified Information Systems Security Professional (CISSP)", "CompTIA Security+", "Certified Ethical Hacker (CEH)"],
        "projects": [
            "Enterprise SIEM Detection Engineering: Built 60+ custom correlation rules in Splunk/Sentinel detecting credential dumping and lateral movement.",
            "Automated Threat Hunting & Playbooks: Developed Python SOAR automation scripts slashing incident triage time by 65%.",
            "Cloud Security Posture Audit: Conducted end-to-end vulnerability assessments and pen-testing across AWS/Azure environments."
        ],
        "academic_projects": [
            "Network Intrusion Detection System: Implemented packet inspection anomaly detector in Python using Scapy.",
            "Malware Sandbox Automation: Built isolated Linux environment dynamically analyzing behavioral process injection."
        ],
        "personal_projects": [
            "CTF Challenge Author: Created open-source web exploitation and binary analysis challenges for university CTFs.",
            "Threat Intel Feed Aggregator: Python tool parsing and deduplicating STIX/TAXII threat feeds."
        ],
        "project_experience_years": 4.0,
        "raw_text": """ELENA ROSTOVA
Reston, VA | elena.rostova@gmail.com | +1 (703) 555-0134
LinkedIn: linkedin.com/in/elenarostova-security | GitHub: github.com/elena-cybersec

PROFESSIONAL SUMMARY
Cybersecurity Analyst & Threat Hunting Specialist with 4 years of experience securing enterprise cloud and on-premise IT environments. Expert in SIEM detection engineering, network traffic analysis, vulnerability management, threat intelligence, and automated incident response.

TECHNICAL EXPERTISE
- Security Operations & SIEM: Splunk, Microsoft Sentinel, CrowdStrike Falcon, Suricata, Zeek, Snort
- Threat Analysis & Hunting: MITRE ATT&CK Framework, Indicator of Compromise (IoC) Extraction, Malware Analysis
- Network & Cloud Security: Firewalls, VPNs, Wireshark, Nmap, TCP/IP Protocols, AWS/Azure Security, Zero-Trust Architecture
- Scripting & Automation: Python, Bash, PowerShell, SOAR Playbooks, SQL

PROFESSIONAL EXPERIENCE
Senior Cybersecurity Analyst | CyberShield Defense (2022 - Present)
- Monitored 24/7 Security Operations Center (SOC) investigating high-severity alerts across 25,000+ corporate endpoints.
- Authored custom SIEM detection rules mapping to MITRE ATT&CK adversary tactics, improving threat detection fidelity by 40%.
- Conducted in-depth forensic investigations of suspected phishing, ransomware, and unauthorized cloud privilege escalation attempts.
- Developed Python automation scripts integrating VirusTotal, AbuseIPDB, and CrowdStrike for automated threat enrichment.

Information Security Analyst | Vanguard Systems (2020 - 2022)
- Performed weekly vulnerability scans using Nessus and coordinated remediation patch workflows across infrastructure teams.
- Analyzed PCAP network captures in Wireshark to identify suspicious exfiltration traffic and C2 beaconing.
- Participated in annual red-team / blue-team exercises and validated compliance against NIST 800-53 and SOC 2 Type II controls.

EDUCATION
B.Sc. in Cybersecurity & Information Assurance | Purdue University (2016 - 2020)

CERTIFICATIONS
- Certified Information Systems Security Professional (CISSP)
- Certified Ethical Hacker (CEH)
- CompTIA Security+"""
    },
    {
        "full_name": "David Kim",
        "email": "david.kim@gmail.com",
        "password": "Password123!",
        "phone": "+1 (415) 555-0163",
        "address": "Berkeley, CA, USA",
        "linkedin": "https://linkedin.com/in/davidkim-datascience",
        "github": "https://github.com/davidkim-data",
        "education": "M.Sc. in Data Science - UC Berkeley (2021)",
        "experience_years": 4.0,
        "filename": "David_Kim_DataScientist_Resume.pdf",
        "skills": [
            "Python", "R", "Machine Learning", "SQL", "Statistics", "Pandas",
            "Apache Spark", "ETL Pipelines", "BigQuery", "Kafka", "Tableau", "Git"
        ],
        "frameworks": ["Pandas", "NumPy", "Scikit-Learn", "XGBoost", "Statsmodels", "PySpark"],
        "tools": ["BigQuery", "Snowflake", "Tableau", "Jupyter", "Apache Spark", "Airflow", "Git", "SQL"],
        "languages": ["Python", "SQL", "R"],
        "certifications": ["Google Professional Data Engineer", "AWS Certified Data Analytics - Specialty"],
        "projects": [
            "Predictive Customer Lifetime Value Model: Formulated gradient boosting models forecasting user retention with 91% accuracy.",
            "Real-Time Analytics Pipeline: Scaled Kafka and Spark streaming jobs processing 10M+ daily events into BigQuery.",
            "A/B Testing Framework: Designed multivariate experimentation platform with automated power calculation and hypothesis testing."
        ],
        "academic_projects": [
            "Bayesian Causal Inference Study: Researched causal effects in observational datasets with inverse probability weighting.",
            "Financial Time-Series Forecaster: Implemented ARIMA and LSTM models predicting volatility indices."
        ],
        "personal_projects": [
            "DataViz Storytelling: Published interactive data visualization essays featured in Towards Data Science.",
            "Automated SQL Query Profiler: Open-source Python script auditing slow queries in PostgreSQL and Snowflake."
        ],
        "project_experience_years": 4.0,
        "raw_text": """DAVID KIM
Berkeley, CA | david.kim@gmail.com | +1 (415) 555-0163
LinkedIn: linkedin.com/in/davidkim-datascience | GitHub: github.com/davidkim-data

PROFESSIONAL SUMMARY
Data Scientist & Quantitative Analyst with 4 years of experience leveraging statistical modeling, machine learning, A/B testing, and distributed big data pipelines (Spark, SQL, Python) to uncover actionable business insights and optimize customer product algorithms.

CORE TECHNICAL SKILLS
- Statistical Analysis & ML: A/B Testing, Hypothesis Testing, Regression, Random Forests, XGBoost, Clustering, Time-Series
- Programming & Libraries: Python (Pandas, NumPy, Scikit-Learn, Statsmodels), R, SQL, PySpark
- Data Platforms & Warehousing: Google BigQuery, Snowflake, PostgreSQL, Apache Spark, Kafka, Airflow
- Visualization & BI: Tableau, PowerBI, Matplotlib, Seaborn, Looker

PROFESSIONAL EXPERIENCE
Senior Data Scientist | MetricFlow Analytics (2022 - Present)
- Designed and analyzed 50+ randomized control trials (A/B tests) driving 18% improvement in customer conversion funnels.
- Built machine learning churn prediction and customer lifetime value (LTV) models deployed into production batch scoring pipelines.
- Partnered with product directors and engineering executives to define core product KPIs, dashboards, and growth metrics.

Data Scientist & Analytics Engineer | QuantData Labs (2021 - 2022)
- Authored complex SQL transformations and Airflow DAGs aggregating petabytes of raw behavioral logs in BigQuery.
- Built automated revenue forecasting models in Python with 94% forecast precision over 90-day horizons.
- Created interactive executive KPI dashboards in Tableau used weekly by C-level leadership.

EDUCATION
M.Sc. in Data Science | University of California, Berkeley (2019 - 2021)
B.Sc. in Applied Statistics & Economics | UCLA (2015 - 2019)

CERTIFICATIONS
- Google Professional Data Engineer
- AWS Certified Data Analytics - Specialty"""
    },
    {
        "full_name": "Emily Watson",
        "email": "emily.watson@gmail.com",
        "password": "Password123!",
        "phone": "+1 (212) 555-0129",
        "address": "New York, NY, USA",
        "linkedin": "https://linkedin.com/in/emilywatson-design",
        "github": "https://github.com/emilywatson-ui",
        "education": "B.A. in Interaction Design - Rhode Island School of Design (RISD) (2020)",
        "experience_years": 4.5,
        "filename": "Emily_Watson_UI_UX_Designer_Resume.pdf",
        "skills": [
            "Figma", "Adobe XD", "Wireframing", "User Research", "Prototyping",
            "Design Systems", "HTML/CSS", "Usability Testing", "Interaction Design"
        ],
        "frameworks": ["Figma Variables & Auto Layout", "Design Tokens", "Material Design 3", "Human Interface Guidelines"],
        "tools": ["Figma", "Adobe XD", "Principle", "Miro", "UserTesting", "Zeplin", "Notion", "HTML/CSS"],
        "languages": ["HTML5", "CSS3/Sass", "Basic JavaScript"],
        "certifications": ["Nielsen Norman Group UX Master Certified (NN/g)", "Interaction Design Foundation (IxDF) Specialist"],
        "projects": [
            "Enterprise Multi-Platform Design System: Created unified tokenized Figma design system used across Web, iOS, and Android apps.",
            "Checkout Redesign & Usability Research: Conducted 30+ moderated user test sessions, driving a 24% reduction in checkout drop-off.",
            "High-Fidelity Interactive Prototyping: Built animated micro-interactions and touch gestures in Figma and Principle."
        ],
        "academic_projects": [
            "Accessible Healthcare Mobile App: Designed WCAG AAA compliant telehealth interface for elderly and low-vision patients.",
            "Smart Home Environmental Dashboard: Conceptualized voice and tactile UI controls for residential energy management."
        ],
        "personal_projects": [
            "Figma Community UI Kit: Free design system UI kit downloaded over 65,000 times by global product designers.",
            "Design Token Generator: Open-source web tool converting Figma style variables into CSS and React props."
        ],
        "project_experience_years": 4.5,
        "raw_text": """EMILY WATSON
New York, NY | emily.watson@gmail.com | +1 (212) 555-0129
Portfolio: emilywatson.design | LinkedIn: linkedin.com/in/emilywatson-design

PROFESSIONAL SUMMARY
Lead UI/UX & Product Designer with 4.5 years of experience crafting intuitive, accessible, and beautifully responsive user interfaces for SaaS web applications, mobile platforms, and enterprise design systems. Master of user research, rapid prototyping, and interaction design.

CORE DESIGN COMPETENCIES
- UX Research & Strategy: User Interviews, Usability Testing, Persona Creation, Journey Mapping, Information Architecture
- UI & Visual Design: Wireframing, High-Fidelity UI, Interactive Prototyping, Micro-Animations, Typography, Color Theory
- Design Systems: Component Libraries, Token Architecture, Auto Layout, Accessibility Compliance (WCAG 2.1 AA/AAA)
- Design Tools: Figma, Adobe XD, Principle, Miro, UserTesting.com, Maze, HTML5/CSS3

PROFESSIONAL EXPERIENCE
Senior Product Designer | PixelCraft Studio (2022 - Present)
- Led end-to-end design for complex B2B SaaS workflow products from discovery research to production handoff.
- Created and maintained a centralized Figma design system with 250+ accessible components, saving 30% of engineering sprint time.
- Conducted remote usability testing sessions and translated qualitative user feedback into high-impact UX improvements.
- Partnered directly with product managers and frontend engineers to ensure pixel-perfect CSS implementation.

UI/UX Designer | AppVantage Digital (2020 - 2022)
- Designed native iOS and Android mobile app interfaces with smooth gesture transitions and intuitive navigation hierarchies.
- Created interactive wireframes and interactive prototypes in Figma for executive stakeholder review and investor pitches.
- Increased onboarding completion rates by 32% through simplified step-by-step progress flows and clearer visual hierarchy.

EDUCATION
B.A. in Interaction Design | Rhode Island School of Design (RISD) (2016 - 2020)

CERTIFICATIONS
- Nielsen Norman Group (NN/g) UX Master Certification
- Interaction Design Foundation (IxDF) Design System Specialist"""
    },
    {
        "full_name": "Liam O'Connor",
        "email": "liam.oconnor@gmail.com",
        "password": "Password123!",
        "phone": "+1 (734) 555-0191",
        "address": "Ann Arbor, MI, USA",
        "linkedin": "https://linkedin.com/in/liamoconnor-embedded",
        "github": "https://github.com/liam-embedded",
        "education": "B.Eng. in Electrical & Computer Engineering - University of Michigan (2020)",
        "experience_years": 4.5,
        "filename": "Liam_OConnor_Embedded_Systems_Resume.pdf",
        "skills": [
            "C", "C++", "RTOS", "Microcontrollers", "Embedded Linux", "I2C/SPI",
            "UART/SPI/I2C", "Device Drivers", "ARM Cortex-M", "FreeRTOS", "PCB Bring-Up", "Git"
        ],
        "frameworks": ["FreeRTOS", "Zephyr OS", "Yocto Project", "Embedded Linux Kernel"],
        "tools": ["JTAG/SWD Debuggers", "Oscilloscopes", "Logic Analyzers", "Keil uVision", "STM32CubeIDE", "Git"],
        "languages": ["C", "C++", "Assembly (ARM)", "Python", "Bash"],
        "certifications": ["ARM Accredited Engineer (AAE)", "Certified Embedded Systems Professional"],
        "projects": [
            "Ultra-Low Power IoT Sensor Node: Developed FreeRTOS firmware achieving 3-year coin-cell battery life with SPI sensor duty cycling.",
            "Automotive CAN Bus Controller Firmware: Wrote deterministic C++ firmware for motor control with sub-millisecond safety interlocks.",
            "Custom Board Bring-Up & BSP: Authored device drivers for I2C power management ICs and SPI flash memory on custom STM32 PCBs."
        ],
        "academic_projects": [
            "Autonomous Quadcopter Flight Controller: Implemented PID stabilization and sensor fusion (Kalman filter) on ARM Cortex-M4.",
            "Hardware Cryptographic Accelerator: Designed AES-128 hardware coprocessor in Verilog on FPGA."
        ],
        "personal_projects": [
            "OpenSource Drone Gimbal Controller: STM32 C++ brushless motor controller with 500+ GitHub stars.",
            "Embedded Linux Driver Guide: Comprehensive tutorials on writing Linux kernel character drivers."
        ],
        "project_experience_years": 4.5,
        "raw_text": """LIAM O'CONNOR
Ann Arbor, MI | liam.oconnor@gmail.com | +1 (734) 555-0191
LinkedIn: linkedin.com/in/liamoconnor-embedded | GitHub: github.com/liam-embedded

PROFESSIONAL SUMMARY
Embedded Systems & Firmware Engineer with 4.5 years of experience writing high-reliability, deterministic C and C++ code for ARM Cortex-M microcontrollers, FreeRTOS, and Embedded Linux environments. Hands-on expertise in peripheral device drivers, hardware bring-up, and bus protocols.

TECHNICAL SKILLS
- Embedded Programming: C, C++ (11/14/17), ARM Assembly, Python (Hardware Test Automation)
- Real-Time OS & Kernels: FreeRTOS, Zephyr OS, Embedded Linux, Yocto, RTOS Task Scheduling
- Hardware Interfaces & Protocols: UART, SPI, I2C, CAN Bus, USB, BLE, Ethernet, GPIO, DMA
- Hardware Tools & Debugging: JTAG/SWD Debuggers, Oscilloscopes, Logic Analyzers, Multimeters, Soldering

PROFESSIONAL EXPERIENCE
Senior Embedded Firmware Engineer | IoT Dynamics Corp (2022 - Present)
- Developed FreeRTOS firmware in C/C++ for battery-powered industrial IoT gateways deployed in harsh environments.
- Wrote low-level device drivers for SPI flash, I2C temperature/pressure sensors, and cellular LTE modems.
- Implemented secure Over-the-Air (OTA) firmware update bootloaders with cryptographic signature validation.
- Performed initial PCB board bring-up, signal integrity validation, and hardware-software boundary debugging.

Embedded Systems Engineer | MicroTech Robotics (2020 - 2022)
- Programmed STM32 (ARM Cortex-M4) microcontrollers controlling multi-axis servo motor actuators with PID feedback.
- Implemented CAN bus communication stack for real-time sensor data exchange with central computer units.
- Conducted hardware bench testing and automated regression test harnesses using Python and serial communication scripts.

EDUCATION
B.Eng. in Electrical & Computer Engineering | University of Michigan (2016 - 2020)

CERTIFICATIONS
- ARM Accredited Engineer (AAE)
- Certified Embedded Systems Professional"""
    },
    {
        "full_name": "Priya Sharma",
        "email": "priya.sharma@gmail.com",
        "password": "Password123!",
        "phone": "+1 (647) 555-0158",
        "address": "Toronto, ON, Canada",
        "linkedin": "https://linkedin.com/in/priyasharma-mobile",
        "github": "https://github.com/priya-mobiledev",
        "education": "B.Sc. in Computer Engineering - University of Waterloo (2020)",
        "experience_years": 4.0,
        "filename": "Priya_Sharma_Mobile_Developer_Resume.pdf",
        "skills": [
            "Flutter", "React Native", "iOS", "Android", "Swift", "Kotlin",
            "REST APIs", "GraphQL", "Firebase", "Git"
        ],
        "frameworks": ["Flutter / Dart", "React Native", "SwiftUI", "Jetpack Compose", "Redux", "Bloc"],
        "tools": ["Xcode", "Android Studio", "Fastlane", "Firebase", "Postman", "Git", "TestFlight"],
        "languages": ["Dart", "Swift", "Kotlin", "TypeScript", "JavaScript"],
        "certifications": ["Google Associate Android Developer", "Meta Certified iOS Developer"],
        "projects": [
            "Cross-Platform FinTech Mobile App: Engineered Flutter application with biometric login and real-time transaction sync for 500k+ users.",
            "Native iOS E-Commerce App: Built SwiftUI client with Apple Pay integration, offline caching, and CoreAnimation transitions.",
            "Automated Mobile CI/CD with Fastlane: Configured Fastlane and GitHub Actions deploying automated builds to TestFlight and Google Play."
        ],
        "academic_projects": [
            "Offline-First GPS Campus Guide: Android application with offline SQLite spatial indexing and turn-by-turn navigation.",
            "Smart Home BLE Controller: iOS Bluetooth Low Energy app pairing with home automation sensors."
        ],
        "personal_projects": [
            "Flutter UI Components Package: Open-source Flutter widget library published on pub.dev with 15k+ downloads.",
            "Personal Habit Tracker App: Published SwiftUI app with 4.8 star rating on Apple App Store."
        ],
        "project_experience_years": 4.0,
        "raw_text": """PRIYA SHARMA
Toronto, ON | priya.sharma@gmail.com | +1 (647) 555-0158
LinkedIn: linkedin.com/in/priyasharma-mobile | GitHub: github.com/priya-mobiledev

PROFESSIONAL SUMMARY
Senior Mobile Application Developer with 4 years of experience building high-performance, beautiful native and cross-platform mobile apps for iOS and Android using Flutter, React Native, Swift, and Kotlin. Adept in state management, offline-first data sync, and mobile release pipelines.

TECHNICAL SKILLS
- Cross-Platform & Hybrid: Flutter (Dart), React Native (TypeScript), Bloc State Management, Redux
- Native iOS & Android: Swift, SwiftUI, UIKit, CoreData, Kotlin, Jetpack Compose, Coroutines, Room
- Backend & Cloud Services: RESTful APIs, GraphQL, Firebase (Auth, Firestore, Cloud Messaging), Apple Pay, Google Pay
- Mobile Tools & CI/CD: Xcode, Android Studio, Fastlane, TestFlight, Google Play Console, Git

PROFESSIONAL EXPERIENCE
Senior Mobile Developer | AppSphere Global (2022 - Present)
- Spearheaded Flutter cross-platform architecture for a mobile digital banking app supporting 500,000+ active monthly users.
- Integrated biometrics authentication (FaceID/TouchID), instant push notifications, and cryptographic token refresh.
- Automated mobile build signing and deployment pipelines using Fastlane, cutting app store release cycles from days to 1 hour.
- Optimized app memory footprint and rendering speed to achieve consistent 60fps animations across budget Android devices.

Mobile Software Engineer | MobileFirst Tech (2020 - 2022)
- Developed native iOS features in Swift/SwiftUI and native Android modules in Kotlin for consumer marketplace applications.
- Implemented offline-first data synchronization layers using SQLite and reactive local caching.
- Collaborated with UX designers to translate complex Figma prototypes into fluid, accessible mobile views.

EDUCATION
B.Sc. in Computer Engineering | University of Waterloo (2016 - 2020)

CERTIFICATIONS
- Google Associate Android Developer
- Meta Certified iOS Developer"""
    },
    {
        "full_name": "Tariq Mansour",
        "email": "tariq.mansour@gmail.com",
        "password": "Password123!",
        "phone": "+1 (312) 555-0174",
        "address": "Chicago, IL, USA",
        "linkedin": "https://linkedin.com/in/tariqmansour-dba",
        "github": "https://github.com/tariq-dba",
        "education": "B.Sc. in Information Technology & Database Systems - University of Illinois (2019)",
        "experience_years": 5.5,
        "filename": "Tariq_Mansour_DBA_Resume.pdf",
        "skills": [
            "PostgreSQL", "MySQL", "Database Tuning", "SQL", "Backup & Recovery",
            "Linux", "Redis", "Python", "Docker", "Git"
        ],
        "frameworks": ["PgBouncer", "ProxySQL", "Patroni High Availability", "Liquibase", "Flyway"],
        "tools": ["PostgreSQL", "MySQL", "Oracle", "MongoDB", "Redis", "Docker", "Linux", "Percona Toolkit", "Datadog"],
        "languages": ["SQL (PL/pgSQL, T-SQL)", "Python", "Bash/Shell"],
        "certifications": ["AWS Certified Database - Specialty", "PostgreSQL Certified Professional (Easiest)", "Oracle Database SQL Certified Associate"],
        "projects": [
            "High-Availability PostgreSQL Cluster: Configured Patroni + Raft distributed consensus cluster with zero data loss automatic failover.",
            "Ultra-High Throughput Database Tuning: Optimized memory buffer parameters and execution plans, increasing TPS by 70%.",
            "Automated Disaster Recovery & Backups: Built automated point-in-time recovery (PITR) pipeline validating backups daily."
        ],
        "academic_projects": [
            "Distributed B-Tree Index Engine: Built multi-core concurrent B-Tree indexing engine in C++.",
            "Relational Query Cost Optimizer: Designed cost-based join ordering simulator in Python."
        ],
        "personal_projects": [
            "pg_query_inspector: Python CLI analyzing pg_stat_statements and suggesting missing indexes.",
            "Docker HA Postgres Stack: Ready-to-use Docker compose cluster with PgBouncer and replica nodes."
        ],
        "project_experience_years": 5.5,
        "raw_text": """TARIQ MANSOUR
Chicago, IL | tariq.mansour@gmail.com | +1 (312) 555-0174
LinkedIn: linkedin.com/in/tariqmansour-dba | GitHub: github.com/tariq-dba

PROFESSIONAL SUMMARY
Senior Database Administrator & Data Platform Architect with 5.5 years of experience managing, securing, and tuning mission-critical PostgreSQL, MySQL, and NoSQL clusters. Expert in query optimization, connection pooling, high-availability replication, and disaster recovery.

TECHNICAL EXPERTISE
- Relational Databases: PostgreSQL (12-16), MySQL, Amazon RDS/Aurora, Oracle Database, SQLite
- NoSQL & In-Memory: Redis, MongoDB, Elasticsearch
- High Availability & Replication: Patroni, PgBouncer, ProxySQL, Streaming Replication, Sharding, Multi-AZ Failover
- Performance Tuning: Query Plan Analysis (EXPLAIN ANALYZE), Index Strategies, Buffer Pool Tuning, VACUUM Optimization
- Automation & OS: Python, Bash Scripting, Linux Kernel System Administration, Docker, Ansible

PROFESSIONAL EXPERIENCE
Lead Database Administrator | Enterprise Data Corp (2022 - Present)
- Administered 60+ production PostgreSQL and MySQL database instances processing over 50,000 transactions per second (TPS).
- Implemented Patroni high-availability clusters and PgBouncer connection pooling, achieving 99.999% database uptime.
- Tuned complex OLTP and reporting queries, eliminating disk-spill sorts and reducing CPU utilization by 40% across clusters.
- Established immutable point-in-time recovery (PITR) pipelines with automated validation testing to meet strict compliance mandates.

Database Administrator & Systems Engineer | FinTech Systems (2019 - 2022)
- Managed MySQL database replication topologies and executed zero-downtime online schema migrations using gh-ost.
- Automated routine database maintenance tasks (vacuuming, reindexing, backups) with Python and cron scripts on Linux.
- Monitored query performance with pg_stat_statements and Datadog, identifying and resolving lock contention bottlenecks.

EDUCATION
B.Sc. in Information Technology & Database Systems | University of Illinois Urbana-Champaign (2015 - 2019)

CERTIFICATIONS
- AWS Certified Database - Specialty
- Oracle Database SQL Certified Associate"""
    },
    {
        "full_name": "Chloe Bennett",
        "email": "chloe.bennett@gmail.com",
        "password": "Password123!",
        "phone": "+1 (206) 555-0188",
        "address": "Seattle, WA, USA",
        "linkedin": "https://linkedin.com/in/chloebennett-qa",
        "github": "https://github.com/chloe-qa-automation",
        "education": "B.Sc. in Computer Science - University of Washington (2020)",
        "experience_years": 4.0,
        "filename": "Chloe_Bennett_QA_Automation_Resume.pdf",
        "skills": [
            "Selenium", "Cypress", "TestNG", "Python", "JIRA", "CI/CD",
            "Playwright", "Jest", "Git", "REST APIs"
        ],
        "frameworks": ["Playwright", "Cypress", "Selenium WebDriver", "PyTest", "TestNG", "Postman / Newman"],
        "tools": ["JIRA", "GitHub Actions", "Jenkins", "Docker", "BrowserStack", "Postman", "k6 Load Testing", "Git"],
        "languages": ["Python", "JavaScript", "TypeScript", "Java", "SQL"],
        "certifications": ["ISTQB Certified Tester - Advanced Level (CTAL-TA)", "Certified Software Test Automation Specialist"],
        "projects": [
            "End-to-End Automated Regression Framework: Built unified Playwright/TypeScript test suite executing 600+ tests in parallel in under 8 minutes.",
            "REST API Automation & Mocking: Developed PyTest framework verifying 200+ API endpoints with schema validation and contract checks.",
            "Performance & Load Testing with k6: Conducted stress tests simulating 50,000 concurrent user sessions before major product launches."
        ],
        "academic_projects": [
            "Mutation Testing Tool: Developed Python tool generating automated test code mutations to assess test suite quality.",
            "Automated Accessibility Validator: Built browser extension evaluating WCAG 2.1 contrast and ARIA tags."
        ],
        "personal_projects": [
            "Playwright Boilerplate Starter: Open-source GitHub test automation template with 600+ stars.",
            "API Mocking Server: Lightweight Node.js mock API for fast local QA testing."
        ],
        "project_experience_years": 4.0,
        "raw_text": """CHLOE BENNETT
Seattle, WA | chloe.bennett@gmail.com | +1 (206) 555-0188
LinkedIn: linkedin.com/in/chloebennett-qa | GitHub: github.com/chloe-qa-automation

PROFESSIONAL SUMMARY
Senior QA & Test Automation Engineer with 4 years of experience designing robust, scalable automated testing frameworks for web applications, REST APIs, and microservice architectures. Expert in Playwright, Cypress, Selenium, Python, and CI/CD quality gates.

TECHNICAL SKILLS
- Test Automation Frameworks: Playwright, Cypress, Selenium WebDriver, PyTest, TestNG, Jest
- API & Performance Testing: Postman, Newman, RestAssured, k6 Load Testing, JMeter
- Continuous Integration & DevOps: GitHub Actions, Jenkins, Docker, BrowserStack, Allure Reports
- Defect Tracking & Agile: JIRA, Confluence, Xray, Agile/Scrum, Test-Driven Development (TDD)
- Programming Languages: Python, TypeScript, JavaScript, Java, SQL

PROFESSIONAL EXPERIENCE
Senior QA Automation Engineer | QualityFirst Software (2022 - Present)
- Architected an end-to-end automated test framework in Playwright and TypeScript, expanding test coverage from 35% to 88%.
- Integrated parallel automated regression suites into GitHub Actions CI/CD pipelines, reducing feedback cycles from 2 hours to 8 minutes.
- Authored automated API test suites using PyTest and Postman, catching critical regression defects before production deployment.
- Led bug triage meetings with engineering leads and product managers, ensuring clear defect reproduction steps in JIRA.

QA Automation Engineer | TechVerify Labs (2020 - 2022)
- Created Cypress automated UI test scripts for customer-facing web portals and e-commerce shopping carts.
- Executed cross-browser and mobile device compatibility testing using BrowserStack and Selenium Grid.
- Conducted performance and load testing using k6, identifying database connection pool saturation points under peak traffic.

EDUCATION
B.Sc. in Computer Science | University of Washington (2016 - 2020)

CERTIFICATIONS
- ISTQB Certified Tester Advanced Level - Test Automation (CTAL-TA)
- Certified Software Test Automation Specialist"""
    }
]

def seed_candidates():
    print(f"Connecting to MongoDB: {DB_NAME}")
    now = datetime.now(timezone.utc)
    resumes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "resumes")
    os.makedirs(resumes_dir, exist_ok=True)

    candidates_count = 0
    resumes_count = 0

    for cand in CANDIDATES_DATA:
        email = cand["email"].lower().strip()
        user_doc = db.users.find_one({"email": email})
        if user_doc:
            user_id = user_doc["_id"]
            db.users.update_one(
                {"_id": user_id},
                {"$set": {
                    "role": "candidate",
                    "full_name": cand["full_name"],
                    "password": hash_pw(cand["password"]),
                    "updated_at": now,
                }}
            )
            print(f"Updated candidate user: {cand['full_name']} ({email})")
        else:
            doc = {
                "role": "candidate",
                "full_name": cand["full_name"],
                "email": email,
                "password": hash_pw(cand["password"]),
                "created_at": now,
            }
            res = db.users.insert_one(doc)
            user_id = res.inserted_id
            print(f"Created candidate user: {cand['full_name']} ({email}) -> ID: {user_id}")
            candidates_count += 1

        # Write actual text file to uploads/resumes/
        txt_filename = cand["filename"].replace(".pdf", ".txt")
        file_path = os.path.join(resumes_dir, txt_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cand["raw_text"])

        # Insert or update Resume document in db.resumes
        existing_resume = db.resumes.find_one({"candidate_id": str(user_id)})
        resume_doc = {
            "candidate_id": str(user_id),
            "filename": cand["filename"],
            "candidate_name": cand["full_name"],
            "email": email,
            "phone": cand.get("phone", ""),
            "address": cand.get("address", ""),
            "linkedin": cand.get("linkedin", ""),
            "github": cand.get("github", ""),
            "skills": cand.get("skills", []),
            "education": cand.get("education", ""),
            "experience_years": cand.get("experience_years", 0),
            "projects": cand.get("projects", []),
            "academic_projects": cand.get("academic_projects", []),
            "personal_projects": cand.get("personal_projects", []),
            "project_experience_years": cand.get("project_experience_years", 0),
            "certifications": cand.get("certifications", []),
            "languages": cand.get("languages", []),
            "tools": cand.get("tools", []),
            "frameworks": cand.get("frameworks", []),
            "raw_text": cand.get("raw_text", ""),
            "updated_at": now,
        }

        if existing_resume:
            db.resumes.update_one({"_id": existing_resume["_id"]}, {"$set": resume_doc})
            resume_id = existing_resume["_id"]
            print(f"  Updated resume record for {cand['full_name']}")
        else:
            resume_doc["created_at"] = now
            res_r = db.resumes.insert_one(resume_doc)
            resume_id = res_r.inserted_id
            print(f"  Inserted resume record for {cand['full_name']} -> ID: {resume_id}")
            resumes_count += 1

    total_candidates = db.users.count_documents({"role": "candidate"})
    total_resumes = db.resumes.count_documents({})
    print("\n==========================================")
    print(f"Successfully seeded IT Candidates and CVs!")
    print(f"Total Candidate Users in DB: {total_candidates}")
    print(f"Total Resume CVs in DB: {total_resumes}")
    print("==========================================\n")

if __name__ == "__main__":
    seed_candidates()
