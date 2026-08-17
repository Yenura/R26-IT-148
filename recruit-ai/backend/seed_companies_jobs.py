"""Seed script to register well-known companies and create real job postings."""
import os
import sys
from datetime import datetime, timezone
import bcrypt
from bson import ObjectId
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("FATAL: MONGODB_URI not set. Copy .env.example to .env and fill credentials.", file=sys.stderr)
    sys.exit(1)
DB_NAME = os.getenv("DB_NAME", "HR")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

COMPANIES_DATA = [
    {
        "company_name": "Google",
        "email": "careers@google.com",
        "password": "Password123!",
        "industry": "Technology / Artificial Intelligence & Cloud",
        "website": "https://careers.google.com",
        "jobs": [
            {
                "title": "Software Engineer",
                "department": "Core Infrastructure & Search",
                "employment_type": "Full-time",
                "location": "Mountain View, CA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's or Master's in Computer Science or equivalent",
                "required_skills": ["Python", "Java", "Git", "REST APIs", "SQL", "Data Structures", "Go"],
                "preferred_skills": ["Distributed Systems", "gRPC", "Kubernetes", "High Scalability"],
                "description": "Join Google's Core Infrastructure engineering team to build high-performance, planet-scale distributed services and search ranking algorithms used by billions daily.",
                "responsibilities": "Design, develop, and maintain robust APIs and backend microservices. Optimize algorithms for latency, scalability, and memory efficiency. Collaborate with cross-functional teams across engineering and UX.",
                "salary_range": "$155,000 - $210,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Machine Learning Engineer",
                "department": "Google DeepMind & Gemini Research",
                "employment_type": "Full-time",
                "location": "Sunnyvale, CA (On-site)",
                "experience_required": 4,
                "education_required": "Master's or Ph.D. in AI, Machine Learning, Computer Science",
                "required_skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Docker", "NLP", "Deep Learning"],
                "preferred_skills": ["Large Language Models (LLMs)", "JAX", "TPU Acceleration", "HuggingFace"],
                "description": "Work at the cutting edge of AI to train and deploy foundational neural network architectures, multi-modal generative models, and intelligent agent workflows.",
                "responsibilities": "Train, fine-tune, and evaluate frontier LLM models. Build scalable MLOps inference pipelines. Optimize inference latency and hardware utilization on TPUs/GPUs.",
                "salary_range": "$175,000 - $240,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Cloud Solutions Architect",
                "department": "Google Cloud Enterprise Solutions",
                "employment_type": "Full-time",
                "location": "New York, NY (Hybrid)",
                "experience_required": 5,
                "education_required": "Bachelor's in Computer Science, Information Systems, or equivalent",
                "required_skills": ["AWS", "Azure", "Cloud Architecture", "Terraform", "Docker", "Microservices", "Kubernetes"],
                "preferred_skills": ["GCP Professional Cloud Architect Certification", "Zero Trust Security", "Serverless"],
                "description": "Design resilient, highly available multi-cloud architectures for Fortune 500 enterprises adopting Google Cloud Platform.",
                "responsibilities": "Lead enterprise cloud modernization and migration strategies. Formulate reference architectures for hybrid-cloud deployments and disaster recovery.",
                "salary_range": "$165,000 - $225,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Site Reliability Engineer (SRE)",
                "department": "Production Platforms",
                "employment_type": "Full-time",
                "location": "Seattle, WA (Hybrid)",
                "experience_required": 4,
                "education_required": "Bachelor's in Computer Science, Systems Engineering, or equivalent",
                "required_skills": ["Kubernetes", "Prometheus", "Linux", "Incident Management", "Python", "Go", "CI/CD"],
                "preferred_skills": ["Grafana", "SLO/SLA Management", "Chaos Engineering", "Distributed Tracing"],
                "description": "Apply software engineering principles to operations problems to ensure 99.999% availability for critical planetary-scale services.",
                "responsibilities": "Automate deployment, observability, and self-healing systems. Lead root-cause analysis (post-mortems) and implement telemetry monitoring.",
                "salary_range": "$160,000 - $215,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
        ],
    },
    {
        "company_name": "Microsoft",
        "email": "careers@microsoft.com",
        "password": "Password123!",
        "industry": "Enterprise Software & Cloud Platforms",
        "website": "https://careers.microsoft.com",
        "jobs": [
            {
                "title": "Full Stack Developer",
                "department": "Microsoft 365 & Copilot Integration",
                "employment_type": "Full-time",
                "location": "Redmond, WA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Computer Science or Software Engineering",
                "required_skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Docker", "Git", "REST APIs"],
                "preferred_skills": ["C#", ".NET Core", "Azure App Services", "GraphQL"],
                "description": "Build modern, accessible web experiences integrating real-time collaboration features and generative AI copilots across Microsoft 365.",
                "responsibilities": "Implement fluid front-end components in React and TypeScript alongside robust back-end APIs. Ensure high performance, accessibility, and unit test coverage.",
                "salary_range": "$145,000 - $195,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "DevOps Engineer",
                "department": "Azure Cloud Infrastructure",
                "employment_type": "Full-time",
                "location": "Austin, TX (Remote)",
                "experience_required": 4,
                "education_required": "Bachelor's Degree in Computer Science or equivalent",
                "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux", "Azure"],
                "preferred_skills": ["GitHub Actions", "Helm", "Ansible", "ArgoCD", "Infrastructure as Code"],
                "description": "Empower hundreds of development teams by building automated continuous delivery pipelines, zero-downtime deployment pipelines, and IaC templates on Azure.",
                "responsibilities": "Standardize CI/CD workflows, manage multi-region Kubernetes clusters, and automate cloud provisioning using Terraform and Bicep.",
                "salary_range": "$150,000 - $200,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Cybersecurity Analyst",
                "department": "Microsoft Threat Intelligence Center (MSTIC)",
                "employment_type": "Full-time",
                "location": "Reston, VA (On-site)",
                "experience_required": 3,
                "education_required": "Bachelor's in Cybersecurity, Computer Science, or equivalent",
                "required_skills": ["Network Security", "SIEM", "Firewalls", "Threat Analysis", "Linux", "Python"],
                "preferred_skills": ["Microsoft Sentinel", "CISSP", "CEH", "Threat Hunting", "Incident Response"],
                "description": "Defend cloud ecosystems against sophisticated cyber adversaries by conducting real-time threat detection, SIEM log analysis, and incident remediation.",
                "responsibilities": "Investigate security alerts, hunt for indicators of compromise (IoCs), and create automated playbooks to thwart adversary tactics.",
                "salary_range": "$135,000 - $180,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "AI/NLP Engineer",
                "department": "Azure AI Services",
                "employment_type": "Full-time",
                "location": "Redmond, WA (Hybrid)",
                "experience_required": 4,
                "education_required": "Master's in Computer Science, Computational Linguistics, or related",
                "required_skills": ["NLP", "Transformers", "HuggingFace", "PyTorch", "LLMs", "Python", "REST APIs"],
                "preferred_skills": ["Retrieval-Augmented Generation (RAG)", "Vector Databases (Pinecone/Milvus)", "LangChain"],
                "description": "Develop and optimize production Natural Language Processing and LLM pipelines powering next-generation enterprise conversational agents.",
                "responsibilities": "Fine-tune Transformer models, build semantic search pipelines with vector embeddings, and integrate RAG architectures into enterprise products.",
                "salary_range": "$165,000 - $220,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
        ],
    },
    {
        "company_name": "Amazon",
        "email": "careers@amazon.com",
        "password": "Password123!",
        "industry": "E-Commerce & AWS Cloud Computing",
        "website": "https://amazon.jobs",
        "jobs": [
            {
                "title": "Backend Developer",
                "department": "AWS Core Services",
                "employment_type": "Full-time",
                "location": "Seattle, WA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Computer Science or Software Engineering",
                "required_skills": ["Node.js", "Python", "REST APIs", "PostgreSQL", "Redis", "Docker", "Java"],
                "preferred_skills": ["AWS DynamoDB", "AWS Lambda", "Distributed Caching", "Microservices"],
                "description": "Build high-throughput, low-latency microservices that power AWS compute, storage, and retail payment checkout workflows.",
                "responsibilities": "Write clean, testable backend code, design schema migrations, implement rate limiting and caching strategies, and maintain zero-latency SLA targets.",
                "salary_range": "$150,000 - $205,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Data Engineer",
                "department": "Amazon Fulfillment Analytics",
                "employment_type": "Full-time",
                "location": "Arlington, VA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Data Science, Computer Science, or Mathematics",
                "required_skills": ["SQL", "Apache Spark", "Python", "ETL Pipelines", "Kafka", "BigQuery", "AWS"],
                "preferred_skills": ["Apache Airflow", "AWS Redshift", "dbt", "Data Lakehouse"],
                "description": "Architect petabyte-scale data pipelines streaming fulfillment center metrics to power global logistics and supply chain optimization.",
                "responsibilities": "Build real-time streaming and batch ETL pipelines using Kafka and Spark. Model dimensional data warehouses and collaborate with BI analysts.",
                "salary_range": "$140,000 - $190,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Database Administrator",
                "department": "AWS Relational Database Services (RDS)",
                "employment_type": "Full-time",
                "location": "San Jose, CA (On-site)",
                "experience_required": 5,
                "education_required": "Bachelor's in Computer Science or Information Technology",
                "required_skills": ["PostgreSQL", "MySQL", "Database Tuning", "SQL", "Backup & Recovery", "Linux"],
                "preferred_skills": ["Amazon Aurora", "Database Sharding", "High Availability / Failover", "Query Optimization"],
                "description": "Manage, tune, and secure mission-critical relational database clusters operating with extreme transaction volumes across global AWS regions.",
                "responsibilities": "Perform query tuning, index optimization, automated backup validation, replication setup, and zero-downtime maintenance updates.",
                "salary_range": "$145,000 - $195,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Frontend Developer",
                "department": "Amazon Prime Experience",
                "employment_type": "Full-time",
                "location": "New York, NY (Hybrid)",
                "experience_required": 2,
                "education_required": "Bachelor's in Computer Science, Graphic/Web Engineering, or equivalent",
                "required_skills": ["React", "JavaScript", "TypeScript", "HTML/CSS", "Redux", "Tailwind"],
                "preferred_skills": ["Next.js", "Web Vitals Optimization", "Accessibility (WCAG 2.1)", "Jest"],
                "description": "Craft lightning-fast, pixel-perfect user interfaces for Amazon Prime members across desktop, tablet, and mobile browsers worldwide.",
                "responsibilities": "Develop modular UI component libraries, optimize Core Web Vitals, implement state management, and conduct A/B performance experiments.",
                "salary_range": "$130,000 - $175,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
        ],
    },
    {
        "company_name": "Meta",
        "email": "careers@meta.com",
        "password": "Password123!",
        "industry": "Social Technology & Metaverse",
        "website": "https://metacareers.com",
        "jobs": [
            {
                "title": "Data Scientist",
                "department": "Instagram Monetization & Growth",
                "employment_type": "Full-time",
                "location": "Menlo Park, CA (Hybrid)",
                "experience_required": 3,
                "education_required": "Master's or Bachelor's in Statistics, Data Science, Economics, or CS",
                "required_skills": ["Python", "R", "Machine Learning", "SQL", "Statistics", "Pandas"],
                "preferred_skills": ["A/B Testing", "Causal Inference", "Tableau", "User Retention Analytics"],
                "description": "Drive product innovation on Instagram by formulating statistical models, leading randomized control trials (A/B testing), and extracting actionable user insights.",
                "responsibilities": "Design statistical experiments, analyze petabytes of behavioral data, formulate econometric user models, and deliver strategic recommendations to leadership.",
                "salary_range": "$155,000 - $210,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Mobile App Developer",
                "department": "WhatsApp Core Mobile",
                "employment_type": "Full-time",
                "location": "San Francisco, CA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Computer Science or Software Engineering",
                "required_skills": ["Flutter", "React Native", "iOS", "Android", "Swift", "Kotlin"],
                "preferred_skills": ["End-to-End Encryption", "Native C++ bridge", "WebSocket Communication", "Performance Profiling"],
                "description": "Deliver seamless, secure messaging and voice/video calling experiences used by over 2 billion people worldwide on iOS and Android platforms.",
                "responsibilities": "Engineer cross-platform and native mobile modules, optimize app startup time and battery drain, and ensure bulletproof offline-first data sync.",
                "salary_range": "$150,000 - $205,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "UI/UX Designer",
                "department": "Reality Labs & Meta Quest",
                "employment_type": "Full-time",
                "location": "Menlo Park, CA (On-site)",
                "experience_required": 3,
                "education_required": "Bachelor's in Interaction Design, HCI, Graphic Design, or equivalent",
                "required_skills": ["Figma", "Adobe XD", "Wireframing", "User Research", "Prototyping"],
                "preferred_skills": ["Spatial Computing Design", "Design Systems", "Usability Testing", "Motion Design"],
                "description": "Pioneer intuitive spatial and 2D interaction paradigms for wearable computing, augmented reality, and virtual reality interfaces.",
                "responsibilities": "Conduct user research studies, build high-fidelity interactive prototypes in Figma, and design scalable cross-platform UI design systems.",
                "salary_range": "$135,000 - $185,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "QA/Test Automation Engineer",
                "department": "Messenger & Video Infrastructure",
                "employment_type": "Full-time",
                "location": "Seattle, WA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Computer Science or Information Technology",
                "required_skills": ["Selenium", "Cypress", "TestNG", "Python", "JIRA", "CI/CD"],
                "preferred_skills": ["Playwright", "Appium", "Load Testing (k6/JMeter)", "Automated Regression Suites"],
                "description": "Build automated quality frameworks ensuring robust reliability and zero regressions across Web, iOS, and Android messaging applications.",
                "responsibilities": "Design end-to-end test automation suites, integrate automated checks into CI/CD pipelines, and collaborate with developers on test-driven development.",
                "salary_range": "$125,000 - $170,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
        ],
    },
    {
        "company_name": "Apple",
        "email": "careers@apple.com",
        "password": "Password123!",
        "industry": "Consumer Electronics & Operating Systems",
        "website": "https://www.apple.com/careers",
        "jobs": [
            {
                "title": "Embedded Systems Engineer",
                "department": "Hardware Technologies / Apple Silicon Firmware",
                "employment_type": "Full-time",
                "location": "Cupertino, CA (On-site)",
                "experience_required": 4,
                "education_required": "Bachelor's or Master's in Electrical Engineering, Computer Engineering, or CS",
                "required_skills": ["C", "C++", "RTOS", "Microcontrollers", "Embedded Linux", "I2C/SPI", "UART/SPI/I2C"],
                "preferred_skills": ["ARM Cortex-M/A", "Device Drivers", "Hardware Debugging (JTAG/Oscilloscope)", "Low-Power Firmware"],
                "description": "Develop low-level bare-metal and RTOS firmware driving cutting-edge Apple Silicon chips and power management sensors in iPhone and Mac hardware.",
                "responsibilities": "Author board bring-up firmware, write high-efficiency peripheral device drivers (SPI, I2C, UART), and debug hardware/software boundary issues with lab test equipment.",
                "salary_range": "$160,000 - $220,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Network Engineer",
                "department": "Apple Global Data Center Infrastructure",
                "employment_type": "Full-time",
                "location": "Austin, TX (On-site)",
                "experience_required": 4,
                "education_required": "Bachelor's in Computer Networking, Telecommunications, or CS",
                "required_skills": ["Cisco", "Routing & Switching", "TCP/IP", "Firewalls", "VPN", "Wireshark", "Linux"],
                "preferred_skills": ["CCNP/CCIE", "BGP / EVPN", "Python Network Automation", "Arista EOS"],
                "description": "Architect, maintain, and optimize the global ultra-low-latency backbone networking infrastructure powering iCloud, Apple Pay, and App Store services.",
                "responsibilities": "Configure high-throughput core routers and switches, monitor global packet routing, mitigate DDoS threats, and automate network telemetry.",
                "salary_range": "$145,000 - $195,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Business/Systems Analyst",
                "department": "Apple Retail Operations & Supply Chain",
                "employment_type": "Full-time",
                "location": "Cupertino, CA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Business Administration, Information Systems, or Engineering",
                "required_skills": ["Requirements Gathering", "SQL", "Agile", "UML", "JIRA", "Business Process"],
                "preferred_skills": ["Process Flow Optimization", "Data Modeling", "Stakeholder Management", "SAP ERP"],
                "description": "Bridge technology and operations by mapping complex retail logistics workflows and translating business needs into technical engineering specifications.",
                "responsibilities": "Gather functional and technical requirements from global retail stakeholders, author comprehensive user stories, and track feature delivery in Agile sprints.",
                "salary_range": "$130,000 - $175,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
            {
                "title": "Blockchain Developer",
                "department": "Apple Pay & Digital Identity Security",
                "employment_type": "Full-time",
                "location": "Sunnyvale, CA (Hybrid)",
                "experience_required": 3,
                "education_required": "Bachelor's in Computer Science or Cryptography",
                "required_skills": ["Solidity", "Ethereum", "Smart Contracts", "Web3.js", "Rust", "Python"],
                "preferred_skills": ["Zero-Knowledge Proofs", "Cryptographic Protocols", "Decentralized ID (DID)", "Secure Enclave"],
                "description": "Research and engineer decentralized identity protocols, verifiable credentials, and cryptographic smart contract systems.",
                "responsibilities": "Develop audited smart contracts and cryptographic libraries, integrate secure cryptographic signing mechanisms, and benchmark transaction throughput.",
                "salary_range": "$155,000 - $215,000 / year",
                "status": "open",
                "interview_required": True,
                "interview_question_count": 10,
            },
        ],
    },
]

def seed():
    print(f"Connecting to MongoDB: {DB_NAME}")
    now = datetime.now(timezone.utc)
    total_companies = 0
    total_jobs = 0

    for comp in COMPANIES_DATA:
        email = comp["email"].lower().strip()
        existing = db.users.find_one({"email": email})
        if existing:
            company_id = existing["_id"]
            db.users.update_one(
                {"_id": company_id},
                {"$set": {
                    "role": "company",
                    "company_name": comp["company_name"],
                    "full_name": comp["company_name"],
                    "industry": comp["industry"],
                    "website": comp["website"],
                    "password": hash_pw(comp["password"]),
                    "updated_at": now,
                }}
            )
            print(f"Updated existing company: {comp['company_name']} ({email})")
        else:
            doc = {
                "role": "company",
                "company_name": comp["company_name"],
                "full_name": comp["company_name"],
                "email": email,
                "password": hash_pw(comp["password"]),
                "industry": comp["industry"],
                "website": comp["website"],
                "created_at": now,
            }
            res = db.users.insert_one(doc)
            company_id = res.inserted_id
            print(f"Created company: {comp['company_name']} ({email}) -> ID: {company_id}")
            total_companies += 1

        # Now handle jobs
        for job_data in comp["jobs"]:
            job_title = job_data["title"]
            # Check if this company already posted this job title
            existing_job = db.jobs.find_one({"company_id": company_id, "title": job_title})
            job_doc = {
                "company_id": company_id,
                "title": job_title,
                "department": job_data.get("department", ""),
                "employment_type": job_data.get("employment_type", "Full-time"),
                "location": job_data.get("location", ""),
                "experience_required": job_data.get("experience_required", 0),
                "education_required": job_data.get("education_required", ""),
                "required_skills": job_data.get("required_skills", []),
                "preferred_skills": job_data.get("preferred_skills", []),
                "description": job_data.get("description", ""),
                "responsibilities": job_data.get("responsibilities", ""),
                "salary_range": job_data.get("salary_range", ""),
                "status": job_data.get("status", "open"),
                "interview_required": job_data.get("interview_required", True),
                "interview_question_count": job_data.get("interview_question_count", 10),
                "updated_at": now,
            }
            if existing_job:
                db.jobs.update_one({"_id": existing_job["_id"]}, {"$set": job_doc})
                print(f"  Updated job: {job_title}")
            else:
                job_doc["created_at"] = now
                res_job = db.jobs.insert_one(job_doc)
                print(f"  Inserted job: {job_title} -> ID: {res_job.inserted_id}")
                total_jobs += 1

    print("\n===============================")
    print(f"Seeding completed successfully!")
    print(f"Total Companies in DB: {db.users.count_documents({'role': 'company'})}")
    print(f"Total Jobs in DB: {db.jobs.count_documents({})}")
    print("===============================\n")

if __name__ == "__main__":
    seed()
