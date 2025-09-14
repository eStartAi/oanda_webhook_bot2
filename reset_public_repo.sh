#!/bin/bash
# Reset and publish a clean public repo snapshot with safety checks, dry run, confirmation, and test 
mode
# Auto-detects python vs python3, prefers local venv if available

# === CONFIG ===
REPO_NAME="oanda_webhook_bot2"
GH_USER="eStartAi"
BRANCH="main"

# === Detect Python (prefer venv) ===
if [ -x "venv/bin/python" ]; then
  PYTHON_CMD="venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_CMD=".venv/bin/python"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
elif command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
else
  echo "❌ Python is not installed. Please install Python 3.x before running."
  exit 1
fi
echo "🐍 Using Python command: $PYTHON_CMD"

# === Function: Safety Check for secrets ===
safety_check() {
  echo "🔎 Running safety check for secrets..."

  # look for common secret patterns
  if find . -type f \( -name "*.py" -o -name "*.txt" -o -name "*.json" -o -name "*.env" \) \
     -exec grep -Ei "(api[_-]?key|secret|token|password|oanda)" {} \; | grep -v ".gitignore" ; then
    echo "❌ Possible secrets detected in files above. Clean them before pushing!"
    exit 1
  fi

  # check if .env file exists
  if [ -f ".env" ]; then
    echo "❌ Found .env file — this must NOT be pushed to public repo."
    exit 1
  fi

  echo "✅ Safety check passed. No obvious secrets found."
}

# === Dry run mode ===
if [ "$1" == "--check" ]; then
  safety_check
  echo "🛑 Dry run complete. Exiting without reset or push."
  exit 0
fi

# === Test mode ===
if [ "$1" == "--test" ]; then
  safety_check
  echo "🧪 Running $PYTHON_CMD main.py ..."
  $PYTHON_CMD main.py
  echo "✅ Test run complete. No publishing performed."
  exit 0
fi

# === STEP 0: Run safety check ===
safety_check

# === Confirm prompt ===
echo "⚠️ You are about to reset the git history and push a clean snapshot."
echo "📂 Current folder: $(pwd)"
read -p "❓ Do you want to continue? (y/N): " confirm
confirm=${confirm,,} # lowercase

if [[ "$confirm" != "y" && "$confirm" != "yes" ]]; then
  echo "🛑 Operation cancelled."
  exit 0
fi

# === STEP 1: Clean Git history ===
echo "🧹 Removing old .git history..."
rm -rf .git

# === STEP 2: Reinitialize repo ===
echo "🔧 Initializing fresh git repo..."
git init
git branch -M $BRANCH

# === STEP 3: Add safe .gitignore ===
echo "🛡️ Writing safe .gitignore..."
cat > .gitignore <<EOL
# Environment & secrets
.env
*.env
.env.*
secrets.json

# Database & logs
trade_logs.db
*.log
logs/

# Virtual environments
venv/
.venv/
ENV/

# Python cache
__pycache__/
*.py[cod]

# System files
.DS_Store
EOL

# === STEP 4: Create repo on GitHub ===
echo "🌐 Creating GitHub repo: $GH_USER/$REPO_NAME ..."
gh repo create $GH_USER/$REPO_NAME --public --confirm || {
  echo "⚠️ Repo may already exist. Skipping creation."
}

# === STEP 5: Push snapshot ===
echo "📤 Adding and pushing snapshot..."
git remote add origin https://github.com/$GH_USER/$REPO_NAME.git
git add .
git commit -m "Initial commit - clean public snapshot"
git push -u origin $BRANCH

echo "✅ Done! Repo available at: https://github.com/$GH_USER/$REPO_NAME"

