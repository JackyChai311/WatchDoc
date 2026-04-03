# 🔒 Post-Edit Verification (强制验证机制)

WatchDoc provides **post-edit verification** to enforce WDP protection rules even when AI ignores the protocol.

---

## 🚀 Quick Setup

### Option A: Git Pre-commit Hook (Recommended)

```bash
# 1. Navigate to your project
cd /path/to/your/project

# 2. Copy the pre-commit hook
cp /path/to/WatchDoc/scripts/hooks/pre-commit .git/hooks/

# 3. Make it executable
chmod +x .git/hooks/pre-commit

# Done! Now every commit will be verified.
```

### Option B: Manual Verification

```bash
# Verify a specific file
watchdoc verify /path/to/project --file src/payment.py

# Verify all files
watchdoc verify /path/to/project
```

---

## 🔍 What It Checks

### 1. FREEZE Module Protection
```
🔒 Detects unauthorized modifications to FREEZE modules
🔒 Checks if temporary authorization exists
🔒 Validates content hash integrity
```

### 2. GUARD Module Assertions
```
⚠️  Validates Signature_Lock assertions
⚠️  Checks complexity limits
⚠️  Verifies test linkage
```

### 3. AUDIT Module Notes
```
📝 Warns if AUDIT module modified without @wd-note
📝 Records all modifications for audit trail
```

---

## 📋 Example Output

### ✅ Passed:
```
🔍 Running WatchDoc pre-commit verification...

✅ WDP verification passed!
```

### ❌ Blocked:
```
🔍 Running WatchDoc pre-commit verification...

❌ WDP VIOLATIONS DETECTED:
   🔒 FREEZE module 'payment_processPayment' was modified without authorization in src/payment.py

🚫 Commit blocked due to WDP violations.
   Grant temporary authorization or revert changes.

   To modify FREEZE modules:
   1. Run: watchdoc grant /path/to/project --module-id=<name> --level=AUDIT --reason="<reason>"
   2. Re-commit your changes
```

---

## 🛡️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│              Pre-commit Verification Flow                    │
└─────────────────────────────────────────────────────────────┘

  User commits changes
         │
         ▼
  ┌─────────────────┐
  │ Git Pre-commit  │
  │     Hook        │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │ 1. Get staged files from git        │
  │ 2. Parse WDP markers from HEAD      │
  │ 3. Parse WDP markers from staged    │
  │ 4. Load temporary authorizations    │
  │ 5. Compare and verify               │
  └────────┬────────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  ✅ PASS    ❌ BLOCK
     │           │
     │           ▼
     │    Print violations
     │    Suggest authorization
     │           │
     │           ▼
     │    Exit with error
     │
     ▼
  Allow commit
```

---

## 🎯 Benefits

| Feature | Description |
|---------|-------------|
| **Zero Trust** | Doesn't rely on AI following protocol |
| **Always On** | Runs automatically on every commit |
| **Clear Feedback** | Tells exactly what's wrong and how to fix |
| **Bypass Available** | Temporary authorization for intentional changes |

---

## ⚠️ Important Notes

### This is NOT a replacement for AI protocol compliance

Post-edit verification is a **safety net**, not a primary enforcement:

| Layer | Protection Type | Coverage |
|-------|-----------------|----------|
| **AI Protocol** | Preventive | During editing |
| **Post-edit Verification** | Reactive | At commit time |

**Both layers are needed for complete protection.**

---

## 📖 CLI Commands

### Verify Project
```bash
watchdoc verify /path/to/project
```

### Verify Specific File
```bash
watchdoc verify /path/to/project --file src/payment.py
```

### Verify with Verbose Output
```bash
watchdoc verify /path/to/project --verbose
```

---

## 🔧 Advanced Configuration

### Custom Hook Location
```bash
# In .watchdoc/config.yaml
hooks:
  pre_commit: true
  pre_commit_path: /custom/path/pre-commit
```

### Skip Verification for Specific Files
```bash
# In .watchdoc/config.yaml
verification:
  skip_files:
    - "*.test.js"
    - "docs/**"
```

---

*Post-edit Verification - Making WDP enforcement stronger*
