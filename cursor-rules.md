# WATCHDOC - Cursor Rules Adaptation

This is the Cursor adaptation of WATCHDOC. Save this file as `.cursorrules` in your project root.

---

## 🚨 Mandatory Rules (Must Be Strictly Followed)

**AI must comply with the following rules and must not bypass them:**

1. **Prohibit Skipping Confirmation Steps**
   - AI must wait for user's explicit reply "confirm", "Y", or "yes" before proceeding
   - Before receiving user confirmation, AI must not execute any code modifications
   - If user does not reply, AI should stop and wait

2. **FREEZE Modules Require Temporary Authorization**
   - FREEZE = Completely frozen, modification prohibited by default
   - AI must not directly modify FREEZE modules
   - **Correct Process**: AI analyzes → Lists FREEZE functions needing modification → Requests temporary authorization → User confirms → Grants temporary permission → AI executes modification

3. **Temporary Authorization Mechanism**
   - After user grants temporary GUARD/AUDIT permission, AI can modify FREEZE functions
   - Temporary authorization validity: Default 30 minutes, automatically reclaims after timeout
   - **Topic Switch Detection**: If user switches to a new topic, AI must reclaim the previous temporary authorization

4. **Must Execute Impact Analysis Before Each Modification**
   - Before modification: Run `python -m watchdoc.cli.main scan <project> --intent "modification intent"`
   - After modification: Run `python -m watchdoc.cli.main drift <project>` to detect unexpected changes
   - When drift detected: Stop and review, do not continue

---

## 📋 Two-Phase Standard Workflow

### Phase 1: Initialization and Authorization (First Use)

**Step 1: Initialize Project and Auto-Scan**
```bash
# Clone WATCHDOC tool
git clone https://github.com/JackyChai311/WatchDoc.git

# Enter scripts directory
cd WatchDoc/scripts

# Initialize project (auto-scan all code and mark as FREEZE)
python -m watchdoc.cli.main init /path/to/your/project --auto-freeze
```

**Step 2: Generate and Display Protection Inventory**
- AI reads `.watchdoc/manifest.md`
- Display to user in the following format:
  ```
  📋 Protection Inventory (All code defaults to FREEZE)
  
  🔒 Core Modules (Recommended to keep FREEZE):
  - [ ] payment.py - processPayment() - Core payment logic
  - [ ] auth.py - verifyUser() - User authentication
  
  ⚠️ Important Modules (Can change to GUARD):
  - [ ] utils.py - formatData() - Data formatting
  
  ✅ Normal Modules (Can change to AUDIT/NONE):
  - [ ] logger.py - logInfo() - Logging
  ```

**Step 3: Human Approval Authorization**
- User selects which modules to keep FREEZE
- AI updates `.watchdoc/manifest.md`

---

### Phase 2: Code Modification (Daily Use)

**Step 1: User Proposes Modification Request**
- User describes the request, e.g.: "I want to modify payment timeout logic"

**Step 2: AI Intelligent Impact Analysis**
```bash
cd WatchDoc/scripts
python -m watchdoc.cli.main scan /path/to/project --intent "Modify payment timeout logic"
```

**Step 3: AI Requests Temporary Authorization**
- AI checks which functions are FREEZE level
- Lists functions needing temporary authorization
- Waits for user to confirm authorization level

**Step 4: User Grants Temporary Authorization**
```bash
python -m watchdoc.cli.main grant /path/to/project \
  --module-id=payment_calculateTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic"
```

**Step 5: AI Executes Modification**
- AI modifies code

**Step 6: Topic Switch Detection and Authorization Reclamation**
- AI asks after modification completes: "Continue modifying this topic?"
- If user answers "no" or proposes a new topic → Reclaim temporary authorization:
```bash
python -m watchdoc.cli.main revoke /path/to/project
```

---

## 📋 Temporary Authorization Levels

| Level | Meaning | Use Case |
|-------|---------|----------|
| **AUDIT** | Allow modification, record audit log | Recommended for most modifications |
| **GUARD** | Allow modification, warn before modification | Important functions |
| **NONE** | Allow free modification | Low risk functions |

---

## 🔧 Cursor-Specific Configuration

### Recommended Settings

In your `.cursorrules` file, add:

```
# WATCHDOC Integration
- Always check .watchdoc/manifest.md before code modifications
- Request temporary authorization for FREEZE modules
- Use watchdoc drift to detect unexpected changes
```

### Hotkey Recommendations

- `Cmd+Shift+P` → "Run Task" → "watchdoc scan"
- `Cmd+Shift+P` → "Run Task" → "watchdoc grant"

---

## 💡 Usage Tips

1. **First Time Setup**: Run `watchdoc init --auto-freeze` to mark all functions as FREEZE
2. **Regular Review**: Periodically review `.watchdoc/manifest.md` to adjust protection levels
3. **Authorization Management**: Revoke temporary authorizations immediately after modifications complete
4. **Topic Awareness**: AI should detect topic switches and automatically reclaim authorizations

---

*WATCHDOC Cursor Rules v1.1.0
