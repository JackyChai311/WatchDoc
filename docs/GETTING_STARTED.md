# Getting Started with WATCHDOC

## Table of Contents
- [Download & Install as IDE Skill](#download--install-as-ide-skill)
- [Installation](#installation)
- [Quick Tutorial](#quick-tutorial)
- [Two-Phase Workflow](#two-phase-workflow)
- [Temporary Authorization Mechanism](#temporary-authorization-mechanism)
- [Common Workflows](#common-workflows)
- [Next Steps](#next-steps)

---

## Download & Install as IDE Skill

### Step 1: Download WATCHDOC

Download from GitHub:

```bash
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
```

### Step 2: Add to Your IDE

1. Open your AI-powered IDE (e.g., Cursor, Windsurf, or any IDE with AI assistant support)
2. Navigate to **Skills** or **Plugins** settings
3. Add the `watchdoc-publish/skill/` directory as a Skill

### Step 3: Deploy WATCHDOC

**Once the Skill is added, simply tell your AI assistant:**

```
Deploy WatchDoc
```

The AI will automatically:
1. Load the WATCHDOC Skill
2. Initialize your project with auto-freeze
3. Generate the protection manifest and index
4. Display the protection summary

### Step 4: Verify Installation

Check that the following files were created:

```bash
ls /path/to/your/project/.watchdoc/
# Should show: manifest.md  index.json
```

You're now ready to use WATCHDOC for AI-safe code governance!

---

## Installation

### From Source

```bash
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
```

### Requirements

- Python 3.8+
- pyyaml>=6.0 (only dependency)

```bash
pip install pyyaml
```

---

## Quick Tutorial

### Step 1: Initialize Your Project with Auto-Freeze

```bash
cd WatchDoc/scripts

# Initialize your project (auto-scan all code and mark as FREEZE)
python -m watchdoc.cli.main init /path/to/your/project --auto-freeze
```

**Output Example:**
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

This will:
- Scan all code files in your project
- **Automatically mark every function as FREEZE**
- Generate `.watchdoc/manifest.md` (human-readable protection inventory)
- Generate `.watchdoc/index.json` (machine-readable index)

### Step 2: Review and Adjust Protection Levels

```bash
# View the generated protection inventory
cat /path/to/your/project/.watchdoc/manifest.md
```

**Example Output:**
```markdown
# WATCHDOC Manifest

**Project:** my-project
**Last Sync:** 2024-04-02 15:30:00
**Total Modules:** 237

## Module Registry

| Module ID | File Location | Lines | Role | Guard | Description | Hash |
|-----------|---------------|-------|------|-------|-------------|------|
| `payment_processPayment` | `payment.py` | `10-50` | Core | FREEZE | Core payment logic | `abc123` |
| `auth_verifyUser` | `auth.py` | `20-45` | Core | FREEZE | User authentication | `def456` |
| `utils_formatData` | `utils.py` | `5-20` | Util | FREEZE | Data formatting | `ghi789` |

## Statistics

- **FREEZE:** 237 modules
- **GUARD:** 0 modules
- **AUDIT:** 0 modules
- **NONE:** 0 modules
```

Manually edit `.watchdoc/manifest.md` or `.watchdoc/index.json` to adjust protection levels:
- **Keep FREEZE**: Core business logic, critical functions
- **Change to GUARD**: Important but modifiable with constraints
- **Change to AUDIT**: Regular features, track changes
- **Change to NONE**: Utility functions, free to modify

### Step 3: Request Modification (Phase 2)

When you need to modify code, analyze the impact first:

```bash
python -m watchdoc.cli.main scan /path/to/project --intent "Modify payment timeout logic"
```

**Output Example:**
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

### Step 4: Grant Temporary Authorization

If you need to modify FREEZE modules:

```bash
python -m watchdoc.cli.main grant /path/to/project \
  --module-id=payment_setTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic"
```

**Output:**
```
✅ Temporary authorization granted
   Module: payment_setTimeout
   Original level: FREEZE
   Temporary level: AUDIT
   Expires at: 2024-04-02T16:00:00
```

### Step 5: Modify Code

After authorization, you can modify the code within the authorized scope.

### Step 6: Revoke Authorization (When Topic Changes)

```bash
# Revoke all temporary authorizations
python -m watchdoc.cli.main revoke /path/to/project
```

---

## Two-Phase Workflow

### Phase 1: Initialization & Authorization (First Time)

```
┌─────────────────────────────────────────────────────────┐
│                    Phase 1: Setup                        │
└─────────────────────────────────────────────────────────┘

1. Initialize Project
   └─> Run: watchdoc init --auto-freeze
   └─> All functions marked as FREEZE
   └─> Generate protection inventory

2. Review Inventory
   └─> Check .watchdoc/manifest.md
   └─> Identify core vs. non-critical modules

3. Adjust Protection Levels
   └─> Keep FREEZE: Core business logic
   └─> Change to GUARD/AUDIT/NONE: Non-critical modules
   └─> Save updated manifest
```

### Phase 2: Code Modification (Daily Use)

```
┌─────────────────────────────────────────────────────────┐
│                 Phase 2: Modification                    │
└─────────────────────────────────────────────────────────┘

1. User Request
   └─> Describe modification intent

2. Impact Analysis
   └─> Run: watchdoc scan --intent "..."
   └─> List directly affected modules (Category A)
   └─> List indirectly affected modules (Category B)

3. Temporary Authorization (if FREEZE modules affected)
   └─> Run: watchdoc grant --module-id=... --level=AUDIT
   └─> Authorization valid for 30 minutes
   └─> Subject to topic switch detection

4. Code Modification
   └─> Modify code within authorized scope
   └─> AI or human executes changes

5. Authorization Reclamation
   └─> Run: watchdoc revoke (when topic changes)
   └─> Or automatic reclamation after 30 minutes
```

---

## Temporary Authorization Mechanism

### Authorization Levels

| Level | Meaning | Use Case | Validity |
|-------|---------|----------|----------|
| **AUDIT** | Allow modification, record audit log | Recommended for most modifications | 30 minutes |
| **GUARD** | Allow modification, warn before modification | Important functions, extra caution | 30 minutes |
| **NONE** | Allow free modification | Low risk functions | 30 minutes |

### Authorization Lifecycle

```
1. Request Phase
   └─> User proposes modification request
   └─> AI analyzes impact
   └─> Lists FREEZE functions needing modification

2. Application Phase
   └─> AI generates temporary authorization request
   └─> User reviews and selects authorization level

3. Grant Phase
   └─> User confirms authorization
   └─> Run: watchdoc grant
   └─> 30-minute countdown starts

4. Execution Phase
   └─> AI modifies code within authorized scope
   └─> All changes recorded to audit log

5. Reclamation Phase
   └─> Automatic: 30-minute timeout
   └─> Manual: watchdoc revoke
   └─> Topic switch: Automatic detection
```

### Topic Switch Detection

If user switches to a different modification topic, authorizations are automatically reclaimed:

```bash
# Current topic: "Modify payment timeout"
watchdoc grant --module-id=payment_setTimeout --level=AUDIT --reason="Modify payment timeout"

# User switches topic: "Add user profile feature"
# Previous authorization is automatically reclaimed
```

---

## Common Workflows

### Workflow 1: Standard AI-Assisted Change

```bash
# 1. Initialize (first time only)
python -m watchdoc.cli.main init /path/to/project --auto-freeze

# 2. Scan for impact
python -m watchdoc.cli.main scan /path/to/project --intent "Modify payment timeout"

# 3. Grant authorization (if FREEZE modules affected)
python -m watchdoc.cli.main grant /path/to/project \
  --module-id=payment_setTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic"

# 4. Check session status
python -m watchdoc.cli.main session /path/to/project

# 5. Modify code (with AI assistance)
# ... your AI-assisted development ...

# 6. Revoke authorization (when topic changes)
python -m watchdoc.cli.main revoke /path/to/project
```

### Workflow 2: Emergency Override

For critical production issues:

```bash
# 1. Create override request
python -m watchdoc.cli.main override \
  --user-id alice \
  --email alice@company.com \
  --scope-type directory \
  --pattern src/payment/ \
  --reason "Emergency payment bug fix" \
  --level dual

# 2. Get request ID: OVR-20240402-0001

# 3. Approve (requires 2 different approvers for dual level)
python -m watchdoc.cli.main approve \
  --request-id OVR-20240402-0001 \
  --user-id bob \
  --email bob@company.com \
  --decision approve

# 4. Make emergency changes
```

### Workflow 3: Check for Code Drift

Detect if code has changed without updating the index:

```bash
python -m watchdoc.cli.main drift /path/to/project
```

**Output:**
```
⚠️ Drift detected!

New modules: 1
  + newModule_newFunction

Modified content: 2
  * payment_processPayment
  * auth_verifyUser

Run: watchdoc reindex to update the index
```

---

## Guard Level Best Practices

### Use FREEZE for:
- Core payment processing
- Authentication logic
- Critical business rules
- Anything that would be catastrophic if broken

### Use GUARD for:
- Configuration files
- Important utility functions
- API interfaces
- Things with tests

### Use AUDIT for:
- Regular features
- Newer code
- Things you're willing to change but want to track

### Use NONE for:
- Brand new features
- Utility helpers
- Experimental code

---

## Platform Adaptations

WATCHDOC supports multiple platforms:

### Pure CLI
See [cli-manual.md](../skill/references/cli-manual.md) for details.

### Cursor IDE
See [cursor-rules.md](../skill/references/cursor-rules.md) for Cursor-specific setup.

### Continue.dev
See [continue-dev.md](../skill/references/continue-dev.md) for Continue.dev integration.

---

## Generated Files

```
your-project/
├── .watchdoc/
│   ├── manifest.md            # Protection inventory (human-readable)
│   ├── index.json             # Index file (machine-readable)
│   ├── temporary_grants.yaml  # Temporary authorization records
│   └── current_session.yaml   # Current session info
└── your-code-files.py         # Code files (containing @wd markers)
```

---

## Next Steps

1. **Read the Protocol Docs**
   - [WDP Protocol](WDP.md) - Marker specification
   - [WGW Protocol](WGW.md) - Governance workflow
   - [API Reference](API.md) - Complete API docs

2. **Initialize Your Project**
   - Run `watchdoc init --auto-freeze`
   - Review the protection inventory
   - Adjust protection levels

3. **Start Using with AI**
   - Request modifications through AI
   - Let AI analyze impact
   - Grant temporary authorizations when needed
   - Verify all changes

---

*WATCHDOC Getting Started Guide v1.1.0
