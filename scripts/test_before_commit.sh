#!/bin/bash

# Pre-commit test script to verify everything is ready for GitHub

echo "🧪 Pre-commit Tests - Bank of Canada MLOps Platform"
echo "=================================================="

ERRORS=0

# Test 1: Check required files exist
echo ""
echo "📁 Checking required files..."
required_files=(
    "README.md"
    "docker-compose.yml"
    ".gitignore"
    "env.example"
    "requirements.txt"
    "docs/INTERVIEW_GUIDE.md"
    "api/main.py"
    "web/package.json"
    "databricks/notebooks/01_economic_data_ingestion.py"
    "databricks/notebooks/02_economic_forecasting_model.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Test 2: Check for secrets in files
echo ""
echo "🔒 Checking for secrets..."
secret_patterns=(
    "sk-[a-zA-Z0-9]"
    "xoxb-[0-9]"
    "ghp_[a-zA-Z0-9]"
    "glpat-[a-zA-Z0-9]"
)

secret_found=false
for pattern in "${secret_patterns[@]}"; do
    if grep -r "$pattern" . --exclude-dir=.git --exclude="*.sh" 2>/dev/null; then
        echo "❌ Potential secret found matching pattern: $pattern"
        secret_found=true
        ERRORS=$((ERRORS + 1))
    fi
done

if [ "$secret_found" = false ]; then
    echo "✅ No obvious secrets found in code"
fi

# Test 3: Check .env file
echo ""
echo "🌐 Checking .env file..."
if [ -f ".env" ]; then
    if grep -q "your_.*_key\|your_.*_id\|your_.*_secret" .env; then
        echo "✅ .env contains placeholder values (good)"
    else
        echo "⚠️  .env may contain real values - review before pushing"
    fi
else
    echo "✅ No .env file found (will be created from env.example)"
fi

# Test 4: Check docker-compose syntax
echo ""
echo "🐳 Checking docker-compose syntax..."
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo "✅ docker-compose.yml syntax is valid"
    else
        echo "❌ docker-compose.yml has syntax errors"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "⚠️  docker-compose not installed, skipping syntax check"
fi

# Test 5: Check file sizes
echo ""
echo "📏 Checking for large files..."
large_files=$(find . -type f -size +10M -not -path "./.git/*" 2>/dev/null)
if [ -z "$large_files" ]; then
    echo "✅ No large files found"
else
    echo "⚠️  Large files found (consider Git LFS):"
    echo "$large_files"
fi

# Test 6: Check Python syntax
echo ""
echo "🐍 Checking Python syntax..."
python_errors=0
if command -v python3 &> /dev/null; then
    for py_file in $(find . -name "*.py" -not -path "./.git/*"); do
        if ! python3 -m py_compile "$py_file" 2>/dev/null; then
            echo "❌ Syntax error in $py_file"
            python_errors=$((python_errors + 1))
        fi
    done
    if [ $python_errors -eq 0 ]; then
        echo "✅ All Python files have valid syntax"
    else
        ERRORS=$((ERRORS + python_errors))
    fi
else
    echo "⚠️  Python3 not found, skipping syntax check"
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
if [ $ERRORS -eq 0 ]; then
    echo "🎉 All tests passed! Ready to commit and push to GitHub."
    echo ""
    echo "Next steps:"
    echo "1. Run: chmod +x scripts/setup_github.sh && ./scripts/setup_github.sh"
    echo "2. Create GitHub repository"
    echo "3. Push your code"
    exit 0
else
    echo "❌ $ERRORS error(s) found. Please fix before committing."
    echo ""
    echo "Common fixes:"
    echo "- Add missing files"
    echo "- Remove or replace any real API keys with placeholders"
    echo "- Fix Python syntax errors"
    echo "- Check docker-compose.yml syntax"
    exit 1
fi
