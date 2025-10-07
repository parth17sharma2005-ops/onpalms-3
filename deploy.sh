#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting PALMS Backend Deployment${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Initialize new repo if needed
if [ ! -d .git ]; then
    echo -e "${BLUE}📦 Initializing git repository...${NC}"
    git init
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo -e "${BLUE}📝 Creating .gitignore...${NC}"
    cat > .gitignore << EOL
__pycache__/
*.pyc
.env
.DS_Store
venv/
.venv/
leads.csv
EOL
fi

# Check if remote exists, if not add it
if ! git remote | grep -q 'origin'; then
    echo -e "${BLUE}🔗 Adding remote origin...${NC}"
    git remote add origin https://github.com/parth17sharma2005-ops/onpalms-4.git
fi

# Stage files
echo -e "${BLUE}📂 Staging files...${NC}"
git add .
git add -f requirements.txt Procfile runtime.txt

# Commit changes
echo -e "${BLUE}💾 Committing changes...${NC}"
git commit -m "Deploy: PALMS Backend $(date +%Y-%m-%d)"

# Push to main branch
echo -e "${BLUE}⬆️ Pushing to remote repository...${NC}"
git push -u origin main --force

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}🌐 Repository: https://github.com/parth17sharma2005-ops/onpalms-4${NC}"
