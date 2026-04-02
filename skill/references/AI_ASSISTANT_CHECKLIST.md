# ✅ AI Assistant Checklist - Before, During, and After Code Modification

## 📋 PRE-MODIFICATION CHECKLIST

**COMPLETE THESE BEFORE MODIFYING ANY CODE:**

- [ ] I have read the full SKILL.md document
- [ ] I have read references/MANDATORY_RULES.md
- [ ] I have verified if WatchDoc is initialized (looked for .watchdoc/)
- [ ] I have scanned for @wd markers in the codebase
- [ ] I have identified all FREEZE level modules
- [ ] I have run or simulated `watchdoc scan` impact analysis
- [ ] I have listed all modules that will be affected
- [ ] I have identified which FREEZE modules need authorization
- [ ] I have requested temporary authorization from the user
- [ ] I have used the exact authorization request format
- [ ] I have received EXPLICIT user confirmation ("yes" / "confirm")
- [ ] I understand what I am allowed to modify
- [ ] I know the authorization boundaries
- [ ] I know what to do if I detect a violation
- [ ] I am ready to stop immediately if needed

**IF ANY BOX IS UNCHECKED:**
- 🔴 STOP - DO NOT PROCEED
- 🟡 Go back and complete the missing steps
- 🟢 Ask the user for guidance if unsure

---

## 📋 DURING-MODIFICATION CHECKLIST

**FOLLOW THESE WHILE MODIFYING CODE:**

- [ ] I am only modifying authorized modules
- [ ] I am staying within the authorized guard level
- [ ] I am recording what I'm changing
- [ ] I am NOT modifying FREEZE modules without authorization
- [ ] I am NOT bypassing any WatchDoc checks
- I am NOT deleting/modifying @wd markers
- [ ] I am adding @wd-note comments where appropriate
- [ ] I am stopping if I detect something wrong
- [ ] I am asking for clarification if unsure
- [ ] I am NOT proceeding with "I think this is okay"

**IF ANY PROBLEM ARISES:**
- 🔴 STOP immediately
- 🟡 Assess the situation
- 🟢 Notify the user before continuing

---

## 📋 POST-MODIFICATION CHECKLIST

**COMPLETE THESE AFTER MODIFYING CODE:**

- [ ] I have run or simulated `watchdoc drift` to verify changes
- [ ] I have verified that only authorized modules were modified
- [ ] I have checked that FREEZE module hashes are intact (if not authorized)
- [ ] I have recorded the modification in the audit log
- [ ] I have documented what was changed
- [ ] I have NOT left any temporary modifications
- [ ] I have NOT deleted any WatchDoc files
- [ ] I have asked the user: "Continue with this topic?"
- I am ready to reclaim authorization if topic switches
- [ ] I know that authorization expires after 30 minutes

**IF ANY ISSUES FOUND:**
- 🔴 Address them before considering the task complete
- 🟡 Notify the user of any problems
- 🟢 Roll back changes if necessary

---

## 🔄 TOPIC SWITCH CHECKLIST

**WHEN USER SWITCHES TO A NEW TOPIC:**

- [ ] I have detected the topic switch
- [ ] I have reclaimed all temporary authorizations
- [ ] I have notified the user: "Authorization reclaimed for previous topic"
- [ ] I have restored FREEZE modules to their original level
- [ ] I have started fresh for the new topic
- [ ] I will go through the PRE-MODIFICATION checklist again for the new topic

**TOPIC SWITCH EXAMPLES:**
- From "Modify payment logic" → "Update README"
- From "Fix login bug" → "Refactor database schema"
- From "Change API endpoint" → "Add new feature X"

**NOT TOPIC SWITCH EXAMPLES:**
- "Also update the error message" (same topic)
- "And fix the typo you found" (same topic)
- "Let's also optimize that while we're at it" (same topic)

---

## ⚠️ VIOLATION RESPONSE CHECKLIST

**IF YOU DETECT A VIOLATION:**

- [ ] I have STOPPED IMMEDIATELY
- [ ] I am NOT continuing with the modification
- [ ] I have assessed what went wrong
- [ ] I have prepared a clear violation report
- [ ] I have notified the user
- I am waiting for user instructions
- [ ] I will NOT resume without explicit user approval
- [ ] I will roll back changes if requested

**VIOLATION REPORT TEMPLATE:**
```
⚠️ WATCHDOC VIOLATION DETECTED

What happened:
- [Describe what was about to happen or happened]
- [List which modules/rules were affected]

Current state:
- I have stopped all operations
- No changes have been made (or changes rolled back)

Next steps:
- Please advise how to proceed
- I will wait for your explicit instruction
```

---

## 📊 QUICK REFERENCE: GUARD LEVELS

| Level | What you can do | Authorization |
|-------|-----------------|---------------|
| **FREEZE** | ❌ No modification | Requires temporary authorization |
| **GUARD** | ⚠️ Must satisfy assertions | Can work within constraints |
| **AUDIT** | ✅ Can modify, add note | Free to modify, just record |
| **NONE** | ✅ Full access | No restrictions |

---

## 🎯 REMINDER: KEY PRINCIPLES

### 🔴 FIRST PRINCIPLE:
**IF YOU'RE UNSURE, STOP AND ASK.**

### 🟡 SECOND PRINCIPLE:
**IT'S BETTER TO ASK FOR PERMISSION THAN FORGIVENESS.**

### 🟢 THIRD PRINCIPLE:
**FOLLOW THE CHECKLIST EXACTLY - NO SHORTCUTS.**

---

## ✅ FINAL CHECK BEFORE TASK COMPLETE

**BEFORE CONSIDERING THE TASK DONE:**

- [ ] All PRE-MODIFICATION checklist items completed
- [ ] All DURING-MODIFICATION checklist items completed
- [ ] All POST-MODIFICATION checklist items completed
- [ ] No violations detected
- [ ] User is aware of what was changed
- [ ] Authorization status is clear
- [ ] Audit trail is complete
- [ ] WatchDoc files are intact
- [ ] User is asked: "Continue with this topic?"

**IF ALL BOXES CHECKED:**
- ✅ Task can be considered complete
- ✅ Ready for next task (if any)

---

*This checklist is part of WatchDoc v1.1.0 - Always use the latest version*
