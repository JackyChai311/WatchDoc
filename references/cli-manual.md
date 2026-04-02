# WATCHDOC - CLI Manual

Pure command-line usage for WATCHDOC, applicable to any editor and IDE.

---

## 📦 Installation

### Method 1: Clone Repository

```bash
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
```

### Method 2: Download Archive

```bash
wget https://github.com/JackyChai311/WatchDoc/archive/refs/heads/main.zip
unzip main.zip
cd WatchDoc-main
```

---

## 🚀 Quick Start

### 1. Initialize Project

```bash
# Enter WATCHDOC directory
cd WatchDoc/scripts

# Initialize your project (auto-scan all code and mark as FREEZE)
python -m watchdoc.cli.main init /path/to/your/project --auto-freeze
```

**Example Output**:
```
✅ Auto-marking complete!
   - Files scanned: 45
   - Functions marked: 237

📊 Language breakdown:
   - python: 89 functions
   - javascript: 67 functions
   - go: 45 functions

✅ Initialization complete: 237 modules indexed
```

### 2. View Protection Inventory

```bash
# View generated manifest file
cat /path/to/your/project/.watchdoc/manifest.md
```

### 3. Human Approval Authorization

Manually edit `.watchdoc/manifest.md` or `.watchdoc/index.json` to modify protection levels.

---

## 📋 Daily Usage

### 1. Scan Modification Impact

```bash
python -m watchdoc.cli.main scan /path/to/project --intent "Modify payment timeout logic"
```

**Example Output**:
```json
{
  "direct_impact": [
    {
      "module_id": "payment_setTimeout",
      "file": "payment.py",
      "guard": "FREEZE",
      "summary": "Set payment timeout"
    }
  ],
  "related_modules": [
    {
      "module_id": "order_processOrder",
      "reason": "Calls payment_setTimeout"
    }
  ]
}
```

### 2. Grant Temporary Authorization

If you need to modify FREEZE modules:

```bash
python -m watchdoc.cli.main grant /path/to/project \
  --module-id=payment_setTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic"
```

**Example Output**:
```
✅ Temporary authorization granted
   Module: payment_setTimeout
   Original level: FREEZE
   Temporary level: AUDIT
   Expires at: 2025-04-02T15:30:00
```

### 3. View Current Session

```bash
python -m watchdoc.cli.main session /path/to/project
```

**Example Output**:
```
============================================================
📊 Current Session Status
============================================================
Session ID: a1b2c3d4
Topic: Modify payment timeout logic
Started at: 2025-04-02T15:20:00
Last activity: 2025-04-02T15:25:00
Status: active
Authorized modules: 2

Authorized functions:
  - payment_setTimeout
    Level: FREEZE → AUDIT
    Expires: 2025-04-02T15:30:00
  - payment_calculateTimeout
    Level: FREEZE → GUARD
    Expires: 2025-04-02T15:30:00
============================================================
```

### 4. Revoke Temporary Authorization

```bash
# Revoke all temporary authorizations
python -m watchdoc.cli.main revoke /path/to/project

# Or revoke single module authorization
python -m watchdoc.cli.main revoke /path/to/project --module-id=payment_setTimeout
```

---

## 🔧 Advanced Features

### Detect Code Drift

```bash
python -m watchdoc.cli.main drift /path/to/project
```

**Example Output**:
```
⚠️ Drift detected!

New modules: 1
  + newModule_newFunction

Modified content: 2
  * payment_processPayment
  * auth_verifyUser
```

### Reindex

```bash
python -m watchdoc.cli.main reindex /path/to/project
```

---

## 📂 Generated Files

```
your-project/
├── .watchdoc/
│   ├── manifest.md           # Protection inventory (human-readable)
│   ├── index.json            # Index file (machine-readable)
│   ├── temporary_grants.yaml # Temporary authorization records
│   └── current_session.yaml  # Current session info
└── your-code-files.py        # Code files (containing @wd markers)
```

---

## 💡 Usage Recommendations

### Using with AI Assistants

If you use AI assistants (like ChatGPT, Claude, etc.), you can:

1. **Initialize Project**: Run `watchdoc init` in terminal
2. **Copy Inventory**: Copy `manifest.md` content to AI
3. **Request Modification**: Let AI analyze impact and tell you which functions need modification
4. **Authorize Modification**: Manually run `watchdoc grant` to grant permission
5. **AI Execution**: Let AI execute modifications
6. **Revoke Authorization**: Run `watchdoc revoke` after modifications complete

### Integration with Git Hooks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for unrevoked temporary authorizations
if [ -f ".watchdoc/temporary_grants.yaml" ]; then
    echo "⚠️ Unrevoked temporary authorizations detected!"
    echo "Please run: cd WatchDoc/scripts && python -m watchdoc.cli.main revoke $(pwd)"
    exit 1
fi

# Detect code drift
cd WatchDoc/scripts && python -m watchdoc.cli.main drift $(pwd)
if [ $? -ne 0 ]; then
    echo "⚠️ Code drift detected, please run reindex first"
    exit 1
fi
```

### Integration with CI/CD

```yaml
# .github/workflows/watchdoc.yml
name: WATCHDOC Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for drift
        run: |
          pip install pyyaml
          cd WatchDoc/scripts && python -m watchdoc.cli.main drift .
      - name: Check for temporary grants
        run: |
          if [ -f ".watchdoc/temporary_grants.yaml" ]; then
            echo "⚠️ Unrevoked temporary authorizations found!"
            exit 1
          fi
```

---

## 🔐 Security Best Practices

1. **Regular Review**: Periodically review `.watchdoc/manifest.md` for protection level appropriateness
2. **Least Privilege**: Only grant temporary authorizations when necessary
3. **Timely Revoke**: Revoke temporary authorizations immediately after modifications complete
4. **Drift Detection**: Regularly run `drift` command to detect unexpected changes

---

*WATCHDOC CLI Manual v1.1.0
