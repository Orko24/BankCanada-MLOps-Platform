#!/bin/bash

# GitHub Setup Script for Bank of Canada MLOps Platform

set -e

echo "🏦 Bank of Canada MLOps Platform - GitHub Setup"
echo "==============================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ -d ".git" ]; then
    print_warning "This directory is already a git repository."
    echo "Do you want to continue? This will add files to the existing repo. (y/N)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        exit 0
    fi
else
    print_status "Initializing git repository..."
    git init
    print_success "Git repository initialized"
fi

# Check if .env exists and warn about secrets
if [ -f ".env" ]; then
    print_warning "Found .env file - checking for secrets..."
    if grep -q "your_.*_key\|your_.*_id\|your_.*_secret" .env; then
        print_warning ".env file contains placeholder values - this is good!"
    else
        print_error "⚠️  SECURITY WARNING: .env file may contain real secrets!"
        echo "Please check .env file and remove any real API keys before pushing to GitHub."
        echo "The .gitignore file will prevent .env from being committed, but double-check!"
        echo ""
        echo "Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            exit 0
        fi
    fi
fi

# Copy GitHub README as main README if user wants
if [ -f "GITHUB_README.md" ]; then
    echo ""
    echo "Do you want to use GITHUB_README.md as your main README.md? (recommended) (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp GITHUB_README.md README.md
        print_success "Updated README.md with GitHub-optimized version"
    fi
fi

# Add all files
print_status "Adding files to git..."
git add .

# Check what's being added
echo ""
echo "Files to be committed:"
git status --porcelain

# Commit
echo ""
echo "Enter commit message (or press Enter for default):"
read -r commit_message
if [ -z "$commit_message" ]; then
    commit_message="Initial commit: Bank of Canada MLOps Platform for technical interview"
fi

git commit -m "$commit_message"
print_success "Files committed to local repository"

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: BankofCanada_project"
echo "   - Description: Bank of Canada MLOps Platform for Technical Interview"
echo "   - Make it Public (to show in your portfolio)"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Push to GitHub:"
echo "   git remote add origin https://github.com/YOURUSERNAME/BankofCanada_project.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Set up secrets for GitHub Actions (optional):"
echo "   - Go to your repo Settings > Secrets and variables > Actions"
echo "   - Add: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, etc."
echo ""
echo "4. Enable GitHub Pages (optional):"
echo "   - Go to Settings > Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main / docs"
echo ""

print_success "Git setup complete! Ready to push to GitHub."
echo ""
echo "📋 Repository URL will be:"
echo "https://github.com/YOURUSERNAME/BankofCanada_project"
echo ""
echo "🎯 For your interview, you can share:"
echo "- Repository URL to show your code"
echo "- Live demo instructions in README.md"
echo "- Documentation in docs/ folder"
