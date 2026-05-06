#!/usr/bin/env python3
"""
Component 2: Quick Start Guide
Run this script to initialize and test the system
"""

import os
import sys
from pathlib import Path

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title):
    print(f"\n{title}")
    print("-"*70)

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required (found {version.major}.{version.minor})")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = ['torch', 'sentence_transformers', 'fastapi', 'pandas', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0, missing

def install_dependencies():
    """Install required packages"""
    print("\nInstalling dependencies...")
    os.system(f"{sys.executable} -m pip install -r backend/requirements.txt")

def run_training():
    """Run ML training pipeline"""
    print("\nRunning ML training pipeline...")
    os.system(f"{sys.executable} ml/train_pipeline.py")

def show_instructions():
    """Show running instructions"""
    print_header("Quick Start Instructions")
    
    print("""
1. START BACKEND (Terminal 1):
   cd component2/backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   
   ✓ API will be available at: http://localhost:8002
   ✓ Swagger docs at: http://localhost:8002/docs
   
2. START FRONTEND (Terminal 2):
   cd component2/frontend
   npm install
   npm run dev
   
   ✓ Frontend will be available at: http://localhost:5173
   
3. TEST ENDPOINTS:
   # Health check
   curl http://localhost:8002/api/v1/interview/health
   
   # Get available jobs
   curl http://localhost:8002/api/v1/interview/jobs
   
   # Start interview
   curl -X POST http://localhost:8002/api/v1/interview/start \\
     -H "Content-Type: application/json" \\
     -d '{
       "candidate_id": "CAND-001",
       "job_role": "Software Engineer",
       "required_skills": ["Java", "SQL"],
       "num_questions": 5
     }'

4. OPEN BROWSER:
   Navigate to http://localhost:5173 to access the interview UI

5. COMPLETE INTERVIEW:
   - Select job role
   - Answer all questions
   - Get results and analysis
""")

def main():
    print_header("Component 2: AI Interview System - Setup Wizard")
    
    # Check Python
    print_section("Checking Python Version")
    if not check_python():
        print("\n❌ Setup failed: Python version incompatible")
        sys.exit(1)
    
    # Check dependencies
    print_section("Checking Dependencies")
    has_deps, missing = check_dependencies()
    
    if not has_deps:
        print_section("Installing Missing Dependencies")
        install_dependencies()
    else:
        print("✓ All dependencies installed")
    
    # Check/create models directory
    print_section("Checking Models Directory")
    models_dir = Path("models")
    if not models_dir.exists():
        print("Models directory not found. Running training pipeline...")
        run_training()
    else:
        models_found = len(list(models_dir.glob("*.json"))) > 0
        if models_found:
            print(f"✓ Models directory exists with {len(list(models_dir.glob('*.json')))} files")
        else:
            print("Models directory empty. Running training pipeline...")
            run_training()
    
    # Show instructions
    show_instructions()
    
    print_header("Setup Complete! ✓")
    print("""
Next steps:
1. Open 2 terminals
2. Run backend: python -m uvicorn main:app --port 8002
3. Run frontend: npm run dev
4. Navigate to http://localhost:5173

For detailed documentation, see README.md
""")

if __name__ == "__main__":
    main()
