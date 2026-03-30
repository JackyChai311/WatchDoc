# Getting Started with WATCHDOG

## Table of Contents
- [Installation](#installation)
- [Quick Tutorial](#quick-tutorial)
- [Adding Your First @wd Marker](#adding-your-first-wd-marker)
- [Common Workflows](#common-workflows)
- [Next Steps](#next-steps)

---

## Installation

### From Source

```bash
git clone https://github.com/JackyChai311/WatchDoc.git
cd watchdog
pip install -e .
```

### Verifying Installation

```bash
watchdog --version
# WATCHDOG 1.1.0
```

---

## Quick Tutorial

### Step 1: Initialize Your Project

```bash
cd /path/to/your/project
watchdog init .
```

This will:
- Scan your code for `@wd` markers
- Generate `.watchdog/manifest.md` (human-readable)
- Generate `.watchdog/index.json` (machine-readable)

### Step 2: Add Your First @wd Marker

Add a protection marker to your code:

```javascript
// @wd: payment-core | Role: Core | Guard: FREEZE | Summary: "Core payment logic - DO NOT MODIFY"
function processPayment(amount, cardInfo) {
    // Core payment logic here
}
// @wd: payment-core | END
```

### Step 3: Re-index

```bash
watchdog init .
```

### Step 4: Try a Scan

```bash
watchdog scan . --intent "Modify payment timeout logic"
```

---

## Adding Your First @wd Marker

### Basic Marker

```python
# @wd: my-module | Role: Core | Guard: GUARD | Summary: "My important module"
def my_function():
    pass
# @wd: my-module | END
```

### With Dependencies

```javascript
// @wd: auth-module | Role: Core | Guard: FREEZE | Depends: crypto-util, db-connector
function authenticateUser(username, password) {
}
// @wd: auth-module | END
```

### With Assertions

```javascript
// @wd: config-module | Role: Config | Guard: GUARD
// @wd-assert: Signature_Lock
const CONFIG = {
    debug: false
};
// @wd: config-module | END
```

---

## Common Workflows

### Workflow 1: Standard AI-Assisted Change

```python
import watchdog

# 1. Initialize
watchdog.init("/path/to/project")

# 2. Create session
session = watchdog.create_session(
    intent="Add new feature",
    user_id="you",
    project_path="/path/to/project"
)

# 3. Analyze impact
impact = watchdog.analyze(session.session_id, "/path/to/project")
print(f"Category A: {len(impact['category_a'])} modules")

# 4. Authorize
for module in impact['category_a']:
    if module['guard'] == 'FREEZE':
        watchdog.authorize(session.session_id, module['module_id'], 1, "/path/to/project")
    else:
        watchdog.authorize(session.session_id, module['module_id'], 3, "/path/to/project")

# 5. Make changes (with AI)
# ... your AI-assisted development ...

# 6. Verify
result = watchdog.verify(session.session_id, "modified_file.py", "/path/to/project")
if result.ok:
    print("✅ Verification passed!")
else:
    print("❌ Violations:", result.violations)
```

### Workflow 2: Emergency Override

```bash
# 1. Create override request
watchdog override --user-id alice --email alice@company.com \
  --scope-type directory --pattern src/payment/ \
  --reason "Emergency payment bug fix" --level dual

# 2. Get request ID: OVR-20240329-0001

# 3. Approve (as bob)
watchdog approve --request-id OVR-20240329-0001 \
  --user-id bob --email bob@company.com \
  --decision approve

# 4. Make your emergency changes

# 5. Verify
watchdog verify /path/to/project modified_file.py
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

## Next Steps

1. **Read the Protocol Docs**
   - [WDP Protocol](WDP.md) - Marker specification
   - [WGW Protocol](WGW.md) - Governance workflow
   - [API Reference](API.md) - Complete API docs

2. **Add @wd Markers**
   - Start with your most critical modules
   - Gradually add to more modules
   - Experiment with different guard levels

3. **Join the Community**
   - GitHub Discussions
   - Discord/Slack server
   - Share your experiences

4. **Contribute**
   - Report issues
   - Suggest features
   - Submit PRs

---

## Troubleshooting

### Q: The `@wd` markers aren't being detected?
A: Make sure the syntax is correct: `// @wd: module-id | Role: X | Guard: Y`

### Q: Verification keeps failing?
A: Check that you're authorizing the correct modules with the right scores

### Q: How do I temporarily bypass protections?
A: Use the emergency override feature with proper approval

---

*Getting Started with WATCHDOG v1.1.0
