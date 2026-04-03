# 🔧 Installation Guide

## 📋 Prerequisites

- Python 3.8+
- Git (for pre-commit hooks)

---

## 🚀 Installation Methods

### Method 1: Install via pip (Recommended)

```bash
# Install from PyPI (coming soon)
pip install watchdoc

# Or install from source
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
pip install -e .
```

### Method 2: Use as IDE Skill

For AI-powered IDEs (Cursor, Windsurf, Coze, etc.):

```bash
# 1. Clone the repository
git clone https://github.com/JackyChai311/WatchDoc.git

# 2. Add to your IDE
# Navigate to Skills/Plugins settings
# Add path: WatchDoc/watchdoc-publish/skill/

# 3. Activate
# Tell your AI: "Deploy WatchDoc"
```

---

## 🔒 Post-Edit Verification Setup

After installing WatchDoc, set up the pre-commit hook:

```bash
# Navigate to your project
cd /path/to/your/project

# Copy the pre-commit hook
cp /path/to/WatchDoc/scripts/hooks/pre-commit .git/hooks/

# Make it executable
chmod +x .git/hooks/pre-commit

# Done! Now every commit will be verified.
```

---

## 📖 Quick Start

### 1. Initialize Your Project

```bash
# Initialize with auto-freeze (all functions marked as FREEZE)
watchdoc init /path/to/your/project --auto-freeze
```

### 2. Review Protection Inventory

```bash
# View the generated manifest
cat /path/to/your/project/.watchdoc/manifest.md

# Adjust protection levels as needed
```

### 3. Grant Temporary Authorization

When you need to modify FREEZE modules:

```bash
watchdoc grant /path/to/project \
  --module-id=payment_processPayment \
  --level=AUDIT \
  --reason="Modify payment timeout logic"
```

### 4. Verify Changes

```bash
# Manual verification
watchdoc verify /path/to/project

# Or let the pre-commit hook verify automatically
git commit -m "Your commit message"
```

---

## 🧪 Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=watchdoc --cov-report=html
```

---

## 📚 Next Steps

- Read [Getting Started Guide](docs/GETTING_STARTED.md)
- Learn [WDP Protocol](docs/WDP.md)
- Understand [WGW Governance](docs/WGW.md)
- Set up [Post-Edit Verification](docs/POST_EDIT_VERIFICATION.md)

---

## ❓ Troubleshooting

### Pre-commit hook not running?

```bash
# Check if the hook is executable
ls -la .git/hooks/pre-commit

# If not, make it executable
chmod +x .git/hooks/pre-commit
```

### Python not found?

```bash
# Make sure Python 3.8+ is installed
python3 --version

# Or use python instead of python3
python --version
```

### Module not found?

```bash
# Make sure WatchDoc is installed
pip install -e .

# Or check your Python path
python3 -c "import watchdoc; print(watchdoc.__file__)"
```

---

*Installation Guide - WatchDoc v1.1.0*
