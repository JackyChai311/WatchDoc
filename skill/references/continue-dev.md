# WATCHDOC - Continue.dev Adaptation

This is the Continue.dev adaptation of WATCHDOC.

---

## Installation Steps

### 1. Clone WATCHDOC Tool

```bash
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
```

### 2. Configure Continue.dev

Create `.continue/config.json` in your project root:

```json
{
  "models": [...],
  "contextProviders": [
    {
      "name": "file",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "watchdoc-init",
      "description": "Initialize WATCHDOC protection for the project",
      "run": "cd /path/to/WatchDoc/scripts && python -m watchdoc.cli.main init ${workspacePath} --auto-freeze"
    },
    {
      "name": "watchdoc-scan",
      "description": "Scan impact of code changes",
      "run": "cd /path/to/WatchDoc/scripts && python -m watchdoc.cli.main scan ${workspacePath} --intent \"${input}\""
    },
    {
      "name": "watchdoc-grant",
      "description": "Grant temporary authorization for FREEZE modules",
      "run": "cd /path/to/WatchDoc/scripts && python -m watchdoc.cli.main grant ${workspacePath} --module-id=${input}"
    },
    {
      "name": "watchdoc-revoke",
      "description": "Revoke all temporary authorizations",
      "run": "cd /path/to/WatchDoc/scripts && python -m watchdoc.cli.main revoke ${workspacePath}"
    }
  ],
  "customCommands": [
    {
      "name": "protect",
      "prompt": "You are a code protection assistant. Follow these rules:\n\n1. Before modifying any code, check if it has @wd markers\n2. If a function is marked as FREEZE, you must:\n   - Inform the user that temporary authorization is needed\n   - Wait for user confirmation\n   - Use /watchdoc-grant to grant authorization\n   - Then proceed with modification\n3. After modification, use /watchdoc-scan to check for related modules\n4. When user changes topic, use /watchdoc-revoke to revoke authorizations"
    }
  ]
}
```

### 3. Create .continuerules File

Create `.continuerules` file in your project root:

```
# WATCHDOC Mandatory Rules

## Prohibit Skipping Confirmation Steps
- AI must wait for user's explicit reply "confirm", "Y", or "yes" before modifying code

## FREEZE Modules Require Temporary Authorization
- FREEZE = Completely frozen, modification prohibited by default
- AI must not directly modify FREEZE modules
- Must request temporary authorization first, only modify after user confirmation

## Temporary Authorization Mechanism
- AI can only modify FREEZE functions after user grants temporary GUARD/AUDIT permission
- Temporary authorization validity: Default 30 minutes
- Automatically reclaim authorization after topic switch

## Verification Process
- Before modification: Use /watchdoc-scan to analyze impact
- After modification: Check modification results
- When issues detected: Stop immediately

## Two-Phase Workflow
1. Initialization: Use /watchdoc-init to initialize project
2. Modification: User request → Analyze impact → Request authorization → User confirms → Execute modification
```

---

## Usage

### Initialize Project

In Continue.dev chat, enter:
```
/watchdoc-init
```

### Scan Impact

```
/watchdoc-scan Modify payment timeout logic
```

### Grant Temporary Authorization

```
/watchdoc-grant payment_calculateTimeout --level=AUDIT --reason="Modify payment timeout logic"
```

### Revoke Authorizations

```
/watchdoc-revoke
```

---

## 💡 Usage Tips

1. **First Time Setup**: Run `/watchdoc-init` to mark all functions as FREEZE
2. **Regular Review**: Periodically review `.watchdoc/manifest.md` to adjust protection levels
3. **Authorization Management**: Revoke temporary authorizations immediately after modifications complete
4. **Topic Awareness**: AI should detect topic switches and automatically reclaim authorizations

---

*WATCHDOC Continue.dev Adaptation v1.1.0
