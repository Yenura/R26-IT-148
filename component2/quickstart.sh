#!/bin/bash
# Component 2: Quick Start Script (Linux/Mac)

echo "=========================================="
echo "Component 2: AI Interview System"
echo "Quick Start"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Backend startup
echo -e "${BLUE}Starting Backend...${NC}"
echo "Run this in Terminal 1:"
echo ""
echo "cd component2/backend"
echo "python -m venv venv"
echo "# Windows PowerShell"
echo ".\venv\Scripts\Activate.ps1"
echo "# Windows CMD"
echo "venv\Scripts\activate.bat"
echo "# macOS/Linux"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo "python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload"
echo ""

# Frontend startup
echo -e "${BLUE}Starting Frontend...${NC}"
echo "Run this in Terminal 2:"
echo ""
echo "cd component2/frontend"
echo "npm install"
echo "npm run dev"
echo ""

# ML Training
echo -e "${YELLOW}First Time Setup:${NC}"
echo "Run this once to generate models:"
echo ""
echo "cd component2/ml"
echo "python train_pipeline.py"
echo ""

echo -e "${GREEN}After starting both services:${NC}"
echo "Open http://localhost:5173 in your browser"
