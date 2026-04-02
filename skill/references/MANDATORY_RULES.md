# 🔴 MANDATORY RULES FOR AI ASSISTANTS

## 🚨 WHEN TO READ THIS DOCUMENT

**READ THIS DOCUMENT BEFORE DOING ANYTHING IF:**
- You are about to modify any code
- The user asks you to change code
- You detect WDP markers in the codebase
- You see a `.watchdoc/` directory
- The project has WatchDoc initialized

---

## 🚨 BEFORE YOU MODIFY ANY CODE - 5 STEPS

### STEP 1: Verify WatchDoc Initialization

First, check if WatchDoc is set up:

```bash
# Look for .watchdoc directory
ls -la .watchdoc/

# Look for WDP markers in code
grep -r "@wd:" . --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.go"
```

If WatchDoc is initialized, **YOU MUST FOLLOW THIS PROTOCOL**.

---

### STEP 2: Run Impact Analysis

**NEVER SKIP THIS STEP.**

```bash
# Run watchdoc scan to analyze impact
watchdoc scan /path/to/project --intent "USER'S ACTUAL REQUEST HERE"
```

**OR** if you can't run the CLI:
- Read `.watchdoc/manifest.md`
- Scan code for `@wd:` markers
- Identify all modules with `Guard: FREEZE`

---

### STEP 3: List Affected Modules

Show the user a clear list **BEFORE** asking for authorization:

```
🔍 IMPACT ANALYSIS RESULTS

📍 DIRECTLY MODIFIED MODULES:
  1. payment.py - processPayment()
     🔒 Protection Level: FREEZE
     📝 Summary: Core payment logic
     📍 Location: src/payment.py (Lines 45-60)

  2. utils.py - formatCurrency()
     🔒 Protection Level: AUDIT
     📝 Summary: Currency formatting utility

🔗 INDIRECTLY AFFECTED MODULES:
  1. order.py - processOrder()
     🔒 Protection Level: FREEZE
     📍 Reason: Calls payment.processPayment()

✅ UNAFFECTED MODULES:
  auth.py, config.py, logger.py
```

---

### STEP 4: Request Temporary Authorization

**THIS STEP IS MANDATORY FOR FREEZE MODULES.**

Use this exact format:

```
======================================================================
📋 TEMPORARY AUTHORIZATION REQUEST
======================================================================

📌 MODIFICATION TOPIC: [User's actual request, e.g., "Modify payment timeout logic"]

The following modules are currently FREEZE (completely frozen) and require your
temporary authorization to modify:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔒 payment_processPayment
   ├─ Function: processPayment()
   ├─ Location: src/payment.py (Lines 45-60)
   ├─ Current Level: FREEZE
   └─ Summary: Core payment logic - DO NOT MODIFY

   💡 Recommended Authorization: AUDIT

   Please select authorization level:
   [ ] AUDIT  - Allow modification, record audit log (Recommended)
   [ ] GUARD  - Allow modification, warn before modification
   [ ] NONE   - Allow free modification (Not recommended)
   [ ] Skip   - Do not authorize this function, keep FREEZE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. 🔒 order_processOrder
   ├─ Function: processOrder()
   ├─ Location: src/order.py (Lines 12-25)
   ├─ Current Level: FREEZE
   └─ Summary: Order processing logic

   💡 Recommended Authorization: GUARD

   Please select authorization level:
   [ ] AUDIT  - Allow modification, record audit log
   [ ] GUARD  - Allow modification, warn before modification (Recommended)
   [ ] NONE   - Allow free modification (Not recommended)
   [ ] Skip   - Do not authorize this function, keep FREEZE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 AUTHORIZATION LEVELS:
• AUDIT: Allow modification, all operations recorded to audit log
• GUARD: Allow modification, warning prompt before modification
• NONE:  Allow free modification, no restrictions (higher risk)

⏰ VALIDITY: Default 30 minutes, automatically reclaims after timeout
🔄 TOPIC SWITCH: If you switch to a new topic, authorization is automatically reclaimed

======================================================================

❓ Please select authorization level individually, or choose batch:
   1. Individual authorization: Select level for each function separately
   2. Batch authorization: Grant AUDIT to all (Recommended)
   3. Batch authorization: Grant GUARD to all
   4. Deny authorization: Keep all functions as FREEZE
======================================================================
```

**WAIT FOR USER REPLY BEFORE PROCEEDING.**

---

### STEP 5: Wait for EXPLICIT User Confirmation

**THIS IS THE MOST IMPORTANT STEP.**

**DO NOT PROCEED UNTIL THE USER REPLIES WITH:**
- "yes"
- "confirm"
- "approve"
- Or explicitly selects authorization levels

**IF USER DOES NOT REPLY:**
- Stop and wait
- Do NOT modify anything
- Do NOT say "I'll do it anyway"
- Do NOT claim "I have implicit permission"

---

## 🚫 THINGS YOU MUST NEVER DO

### ❌ NEVER DO THESE:

1. **NEVER** skip reading this document
2. **NEVER** skip the impact analysis step
3. **NEVER** modify FREEZE modules without temporary authorization
4. **NEVER** modify code before user confirmation
5. **NEVER** say "I can do it without authorization"
6. **NEVER** hide violation reports from user
7. **NEVER** claim "The user didn't say I couldn't"
8. **NEVER** continue after authorization expires
9. **NEVER** bypass WatchDoc checks
10. **NEVER** delete or modify `.watchdoc/` without explicit permission

---

## ✅ THINGS YOU MUST ALWAYS DO

### ✅ ALWAYS DO THESE:

1. **ALWAYS** read this document before modifying code
2. **ALWAYS** run impact analysis first
3. **ALWAYS** list affected FREEZE modules
4. **ALWAYS** request temporary authorization
5. **ALWAYS** wait for explicit user confirmation
6. **ALWAYS** verify changes after modification
7. **ALWAYS** record audit logs
8. **ALWAYS** ask if user wants to continue the same topic
9. **ALWAYS** reclaim authorization when topic switches
10. **ALWAYS** stop immediately if you detect a violation

---

## 🚨 IF YOU DETECT A VIOLATION

### If you realize you are violating or about to violate these rules:

1. **STOP IMMEDIATELY** - Do not proceed
2. **Report the violation** to the user clearly
3. **Explain what happened** - Be transparent
4. **Wait for user instructions** - Do not guess
5. **Roll back if needed** - If modification already happened

**Example violation report:**
```
⚠️ VIOLATION DETECTED

I was about to modify a FREEZE module without authorization.

Module: payment_processPayment
Current Level: FREEZE
What I was about to do: Modify timeout logic

I have stopped. Please advise how to proceed.
```

---

## 📋 REMINDER: THE 5-STEP CHECKLIST

Before modifying ANY code:

- [ ] Step 1: Verify WatchDoc initialization
- [ ] Step 2: Run impact analysis
- [ ] Step 3: List affected modules
- [ ] Step 4: Request temporary authorization
- [ ] Step 5: Wait for EXPLICIT user confirmation

**IF ANY BOX IS UNCHECKED, STOP AND DO NOT PROCEED.**

---

## 🎯 FINAL NOTE

**WatchDoc exists to protect code.**

Following this protocol:
- Prevents accidental damage to core logic
- Creates an audit trail of modifications
- Builds trust between you and the user
- Ensures code changes are intentional and authorized

**When in doubt: STOP and ASK.**

---

*Last updated: WatchDoc v1.1.0*
