#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}FastAPI Project Quick Start${NC}"
echo -e "${GREEN}================================${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created. Please update with your settings if needed.${NC}"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "\n${YELLOW}To run the application:${NC}"
echo -e "1. Start MySQL and Redis"
echo -e "2. Run: ${GREEN}uvicorn app.main:app --reload${NC}"
echo -e "3. Run Celery worker: ${GREEN}celery -A app.tasks.celery_app worker --loglevel=info${NC}"
echo -e "\n${YELLOW}Or use Docker:${NC}"
echo -e "${GREEN}docker-compose up${NC}"
echo -e "\n${YELLOW}API will be available at:${NC} http://localhost:8000"
echo -e "${YELLOW}API Docs:${NC} http://localhost:8000/docs"
