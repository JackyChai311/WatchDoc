---
name: watchdoc-gateway
description: WATCHDOC AI-Native Code Governance & Security Gateway System; Two-phase intelligent workflow: Phase 1 - AI auto-scans all code and FREEZE everything, generates inventory for human approval; Phase 2 - When modifying code, AI analyzes impact and lists modules, human confirms before execution; Use when protecting core code in AI-assisted programming, implementing tiered authorization, verifying code changes, or establishing AI code governance framework
dependency:
  python:
    - pyyaml>=6.0
---

# WATCHDOC Gateway - Two-Phase Intelligent Workflow

## ⚠️ Mandatory Rules (Must Be Strictly Followed)

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
   - Before modification: Run `watchdoc scan` to analyze impact
   - After modification: Run `watchdoc drift` to detect unexpected changes
   - When drift detected: Review changes before continuing

5. **Two-Phase Workflow Cannot Be Skipped**
   - Phase 1: Initialize → Generate inventory → Wait for user selection → Save
   - Phase 2: User request → Analyze impact → **Request temporary authorization** → Wait for user confirmation → Execute modification
   - Any "wait for user confirmation" step cannot be skipped

6. **Violation Handling**
   - If AI detects itself violating the above rules
   - Must immediately stop all modification operations
   - Report violations to user
   - Wait for user's explicit instructions

---

## 🚨 Important Notice

**The core value of this SKILL is the "temporary authorization mechanism"!**

**Key Process**:
- ❌ Modifying without waiting for confirmation = Serious violation
- ❌ Directly modifying FREEZE modules = Serious violation
- ✅ Request temporary authorization → User confirms → Execute modification = Correct process

**Lifecycle of Temporary Authorization**:
1. User proposes modification request
2. AI analyzes and lists FREEZE functions needing modification
3. AI requests temporary authorization (GUARD/AUDIT)
4. User confirms authorization
5. AI executes modification
6. **Authorization maintained**: If continuing to modify the same topic
7. **Authorization reclaimed**: If switching to a new topic

---

## Task Objectives
- This Skill is for: AI-native code governance and protection, preventing AI from mistakenly modifying core logic
- Core workflow:
  - **Phase 1**: Initialize → Auto-scan all code → FREEZE everything → Generate inventory → Human approval authorization
  - **Phase 2**: User request → AI analyzes impact → Lists affected functions → Human confirms → Execute modification
- Capabilities include: Auto-scanning, intelligent impact analysis, human-in-the-loop authorization, code verification
- Trigger conditions: When users need to protect core code in AI-assisted programming, implement tiered authorization, or verify code changes

## Prerequisites

### Environment Requirements
- Python 3.8+
- No external dependencies (uses standard library only)

### Supported Languages (18+ Programming Languages)

WATCHDOC supports automatic function recognition and protection for the following programming languages:

| Language | Extension | Code Block Type | Comment Style |
|----------|-----------|----------------|---------------|
| **Python** | `.py` | Indentation | `#` |
| **JavaScript** | `.js`, `.jsx`, `.mjs` | Braces `{}` | `//` |
| **TypeScript** | `.ts`, `.tsx` | Braces `{}` | `//` |
| **Java** | `.java` | Braces `{}` | `//` |
| **Go** | `.go` | Braces `{}` | `//` |
| **Rust** | `.rs` | Braces `{}` | `//` |
| **Ruby** | `.rb`, `.rake` | Keyword `end` | `#` |
| **PHP** | `.php` | Braces `{}` | `//` |
| **C/C++** | `.c`, `.cpp`, `.h`, `.hpp` | Braces `{}` | `//` |
| **C#** | `.cs` | Braces `{}` | `//` |
| **Swift** | `.swift` | Braces `{}` | `//` |
| **Kotlin** | `.kt`, `.kts` | Braces `{}` | `//` |
| **Scala** | `.scala` | Braces `{}` | `//` |
| **Bash** | `.sh`, `.bash` | Braces `{}` | `#` |
| **Lua** | `.lua` | Keyword `end` | `--` |
| **Perl** | `.pl`, `.pm` | Braces `{}` | `#` |
| **R** | `.r`, `.R` | Braces `{}` | `#` |

**Auto-detection**: Language type is automatically recognized based on file extension.

## Two-Phase Standard Workflow

### Phase 1: Initialization and Authorization (First Use)

**Step 1: Initialize Project and Auto-Scan**
- Call `python -m watchdoc.cli.main init /path/to/project --auto-freeze`
- AI automatically scans all code files
- **Automatically mark each function/module with FREEZE protection level**
- Generate protection inventory `.watchdoc/manifest.md`

**Step 2: Generate and Display Protection Inventory**
- AI reads `.watchdoc/manifest.md`
- Display to user in the following format:
  ```
  📋 Protection Inventory (All code defaults to FREEZE)
  
  🔒 Core Modules (Recommended to keep FREEZE):
  - [ ] payment-processing.py - processPayment() - Core payment logic
  - [ ] auth.py - verifyUser() - User authentication
  
  ⚠️ Important Modules (Can change to GUARD):
  - [ ] utils.py - formatData() - Data formatting
  - [ ] api.py - sendRequest() - API calls
  
  ✅ Normal Modules (Can change to AUDIT/NONE):
  - [ ] logger.py - logInfo() - Logging
  - [ ] config.py - loadConfig() - Configuration loading
  ```

**Step 3: Human Approval Authorization**
- User selects which modules to keep FREEZE
- Which to change to GUARD/AUDIT/NONE
- AI updates `.watchdoc/manifest.md`

---

### Phase 2: Code Modification (Daily Use)

**Step 1: User Proposes Modification Request**
- User describes the request, e.g.: "I want to modify payment timeout logic"

**Step 2: AI Intelligent Impact Analysis (Phase 1)**
- Call `python -m watchdoc.cli.main scan /path/to/project --intent "user request"`
- AI analyzes and lists:
  ```
  🎯 Impact Analysis Report
    
  ═══════════════════════════════════════
  
  📍 Directly Modified Modules (Category A):
  
  1. payment.py - setTimeout()
     🔒 Protection level: GUARD
     📍 Location: Lines 45-60
     📝 Function: Set payment timeout duration
     ⚠️ Dependencies: Called by order.py, checkout.py
  
  ═══════════════════════════════════════
  
  🔗 Indirectly Affected Modules (Category B):
  
  1. order.py - processOrder()
     🔒 Protection level: FREEZE
     📍 Reason: Calls payment.setTimeout()
  
  2. checkout.py - completeCheckout()
     🔒 Protection level: FREEZE
     📍 Reason: Calls payment.setTimeout()
  
  ═══════════════════════════════════════
  
  ✅ Unaffected Modules (Category C):
     auth.py, database.py, logger.py, config.py
     Total 4 modules
  ```

**Step 3: AI Requests Temporary Authorization**
- AI checks which functions are FREEZE level and need temporary authorization:
  ```
  ======================================================================
  📋 Temporary Authorization Request
  ======================================================================
  
  📌 Modification Topic: Modify payment timeout logic
  
  The following functions are currently FREEZE (completely frozen) and require your temporary authorization to modify:
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  1. 🔒 payment_calculateTimeout
     ├─ Function: Calculate timeout duration
     ├─ Location: payment.py (Lines 45-60)
     └─ Current level: FREEZE
  
     💡 Recommended authorization: AUDIT
  
     Please select authorization level:
     [ ] AUDIT  - Allow modification, record audit log (Recommended)
     [ ] GUARD  - Allow modification, warn before modification
     [ ] NONE   - Allow free modification (Not recommended)
     [ ] Skip   - Do not authorize this function, keep FREEZE
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  2. 🔒 payment_setTimeout
     ├─ Function: Set timeout parameters
     ├─ Location: payment.py (Lines 65-75)
     └─ Current level: FREEZE
  
     💡 Recommended authorization: GUARD
  
     Please select authorization level:
     [ ] AUDIT  - Allow modification, record audit log
     [ ] GUARD  - Allow modification, warn before modification (Recommended)
     [ ] NONE   - Allow free modification (Not recommended)
     [ ] Skip   - Do not authorize this function, keep FREEZE
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  📊 Authorization Level Description:
  • AUDIT: Allow modification, all operations recorded to audit log
  • GUARD: Allow modification, warning prompt before modification
  • NONE:  Allow free modification, no restrictions (higher risk)
  
  ⏰ Validity Period: Default 30 minutes, automatically reclaims after timeout
  🔄 Topic Switch: If you switch to a new topic, authorization will be automatically reclaimed
  
  ======================================================================
  
  ❓ Please select authorization level individually, or choose batch authorization:
     1. Individual authorization: Select level for each function separately
     2. Batch authorization: Grant AUDIT to all (Recommended)
     3. Batch authorization: Grant GUARD to all
     4. Deny authorization: Keep all functions as FREEZE
  ======================================================================
  ```

**Step 4: User Grants Temporary Authorization**
- User selects authorization method:
  
  **Method A: Individual Authorization**
  ```
  User: payment_calculateTimeout grant AUDIT
        payment_setTimeout grant GUARD
  ```
  
  **Method B: Batch Authorization**
  ```
  User: Grant AUDIT to all
  ```
  
  **Method C: Deny Authorization**
  ```
  User: Deny authorization, keep FREEZE
  ```

- AI calls CLI to grant permission based on user selection:
  ```bash
  watchdoc grant /project \
    --module-id=payment_calculateTimeout \
    --level=AUDIT \
    --reason="Modify payment timeout logic"
  ```
- AI records temporary authorization, starts 30-minute countdown

**Step 5: AI Executes Modification**
- AI modifies code
- AI records modification history

**Step 6: Topic Switch Detection and Authorization Reclamation**
- AI asks after modification completes: "Continue modifying this topic?"
- If user answers "yes" or continues to propose related requests → Authorization maintained
- If user answers "no" or proposes a new topic → AI automatically reclaims temporary authorization:
  ```
  🔄 Topic switch detected
  
  Reclaiming previous temporary authorization:
  - payment_calculateTimeout (FREEZE) ✓
  - payment_setTimeout (FREEZE) ✓
  
  All temporary authorizations have been reclaimed, functions restored to FREEZE level.
  ```

---

## 📋 Temporary Authorization Mechanism Details

### Authorization Level Description

| Level | Meaning | Applicable Scenarios | Validity Period |
|-------|---------|---------------------|-----------------|
| **AUDIT** | Allow modification, record audit log | Recommended, applicable to most modifications | 30 minutes |
| **GUARD** | Allow modification, warn before modification | Important functions, need extra caution | 30 minutes |
| **NONE** | Allow free modification, no restrictions | Low risk functions, fully trusted scenarios | 30 minutes |

### Authorization Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│           Temporary Authorization Lifecycle              │
└─────────────────────────────────────────────────────────┘

1. Request Phase
   └─> User proposes modification request
   └─> AI analyzes impact
   └─> Lists FREEZE functions needing modification

2. Application Phase
   └─> AI generates temporary authorization request report
   └─> User reviews and selects authorization level

3. Grant Phase
   └─> User confirms authorization
   └─> AI calls CLI to grant temporary permission
   └─> Start 30-minute countdown

4. Execution Phase
   └─> AI modifies code within authorized scope
   └─> Real-time verification of constraints
   └─> Record audit logs

5. Maintenance/Reclamation Phase
   └─> If same topic continues: Authorization maintained
   └─> If topic switches: Automatically reclaim authorization
   └─> If timeout: Automatically reclaim authorization
```

### Authorization Record Format

All temporary authorizations are recorded in `.watchdoc/temporary_grants.json`:

```json
{
  "session_id": "SESSION-20240402-153000",
  "topic": "Modify payment timeout logic",
  "grants": [
    {
      "module_id": "payment_calculateTimeout",
      "original_level": "FREEZE",
      "temporary_level": "AUDIT",
      "granted_at": "2024-04-02T15:30:00Z",
      "expires_at": "2024-04-02T16:00:00Z",
      "reason": "Modify payment timeout logic"
    }
  ],
  "status": "active"
}
```

---

## Resource Index

### Necessary Scripts

#### Core Scripts
- **CLI Entry**: Run via `python -m watchdoc.cli.main`
  - Purpose: Command-line interface entry point
  - Commands: init, scan, grant, revoke, session, verify

#### WDP Layer
- **Parser**: [scripts/watchdoc/wdp/parser.py](scripts/watchdoc/wdp/parser.py)
  - Purpose: Parse @wd markers
- **Auto Marker**: [scripts/watchdoc/wdp/auto_marker.py](scripts/watchdoc/wdp/auto_marker.py)
  - Purpose: Automatically add @wd markers to code
- **Verifier**: [scripts/watchdoc/wdp/verifier.py](scripts/watchdoc/wdp/verifier.py)
  - Purpose: Verify code changes

#### WGW Layer
- **Manifest Manager**: [scripts/watchdoc/wgw/manifest.py](scripts/watchdoc/wgw/manifest.py)
  - Purpose: Manage protection inventory
- **Authorization Manager**: [scripts/watchdoc/wgw/authorization.py](scripts/watchdoc/wgw/authorization.py)
  - Purpose: Manage authorization sessions
- **Temporary Grant Manager**: [scripts/watchdoc/wgw/temporary_grant.py](scripts/watchdoc/wgw/temporary_grant.py)
  - Purpose: Manage temporary authorization
- **Override Manager**: [scripts/watchdoc/wgw/override.py](scripts/watchdoc/wgw/override.py)
  - Purpose: Manage emergency override requests

#### Index Layer
- **Impact Analyzer**: [scripts/watchdoc/index/analyzer.py](scripts/watchdoc/index/analyzer.py)
  - Purpose: Analyze modification impact, perform A/B/C classification

### Domain References

- **CLI Manual**: See [references/cli-manual.md](references/cli-manual.md)
  - When to read: When using CLI commands
- **Cursor Rules**: See [references/cursor-rules.md](references/cursor-rules.md)
  - When to read: When integrating with Cursor IDE
- **Continue.dev**: See [references/continue-dev.md](references/continue-dev.md)
  - When to read: When integrating with Continue.dev

---

## Important Notes

### AI Agent Responsibilities

**MUST DO**:
- ✅ Follow two-phase workflow strictly
- ✅ Wait for user confirmation before modifying code
- ✅ Request temporary authorization for FREEZE modules
- ✅ Verify all code changes
- ✅ Record audit logs
- ✅ Detect topic switches and reclaim authorization

**MUST NOT DO**:
- ❌ Skip any confirmation steps
- ❌ Directly modify FREEZE modules without authorization
- ❌ Ignore verification failures
- ❌ Continue modifications after authorization expires
- ❌ Hide violation reports from user

### Error Handling

If any of the following situations occur, immediately stop and wait for user instruction:

1. **Authorization expired**: Temporary authorization has exceeded 30-minute validity period
2. **Verification failed**: Code changes violate WDP constraints
3. **Topic switch detected**: User has switched to a new modification topic
4. **Violation detected**: AI detects itself violating rules

### Platform Adaptation

WATCHDOC SKILL supports multiple platforms:

- **Coze**: Directly load this SKILL
- **Cursor**: See [references/cursor-rules.md](references/cursor-rules.md)
- **Continue.dev**: See [references/continue-dev.md](references/continue-dev.md)
- **Pure CLI**: See [references/cli-manual.md](references/cli-manual.md)

---

## Usage Examples

### Example 1: Initialize Project

```bash
# Initialize project and auto-scan all code
watchdoc init /path/to/project --auto-freeze

# Result: All functions marked as FREEZE, generated .watchdoc/manifest.md
```

### Example 2: Request Temporary Authorization

```bash
# Grant temporary AUDIT permission
watchdoc grant /path/to/project \
  --module-id=payment_calculateTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic" \
  --topic="Payment timeout optimization"
```

### Example 3: Check Session Status

```bash
# View current temporary authorization status
watchdoc session /path/to/project

# Output:
# Session ID: SESSION-20240402-153000
# Topic: Payment timeout optimization
# Active Grants:
#   - payment_calculateTimeout (AUDIT, 25 minutes remaining)
```

### Example 4: Reclaim Authorization

```bash
# Reclaim specific authorization
watchdoc revoke /path/to/project --module-id=payment_calculateTimeout

# Or reclaim all authorizations
watchdoc revoke /path/to/project
```

---

*WATCHDOC Gateway v1.1.0 - AI-Native Code Governance System
