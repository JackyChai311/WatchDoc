# WGW Protocol Specification v1.1

> Watchdog Gateway - Human-in-the-Loop AI Code Governance Protocol

## Table of Contents
- [Overview](#overview)
- [Standard Workflow](#standard-workflow)
- [A/B/C Classification](#abc-classification)
- [Authorization Scoring](#authorization-scoring)
- [Emergency Override](#emergency-override)
- [Manifest Management](#manifest-management)
- [Drift Detection](#drift-detection)

---

## Overview

**WGW (Watchdog Gateway) is a human-in-the-loop governance protocol that enables controlled AI-assisted programming while protecting critical code.

### Core Principles:
- **Default Deny**: Code is read-only by default
- **Human-in-the-Loop**: Humans have final decision on critical changes
- **Impact-aware**: Smart impact analysis before changes
- **Auditable**: All actions are recorded and traceable

---

## Standard Workflow

### Phase 1: Initialization

```
User Code → WDP Parser → Manifest Generation → Protection Inventory
```

**Steps**:
1. Run `watchdog init /path/to/project`
2. System scans for `@wd` markers
3. Generates `.watchdog/manifest.md` and `index.json`
4. Human reviews protection level settings

### Phase 2: Impact Analysis

```
User Intent → Semantic Matching → Call Graph Analysis → A/B/C Classification
```

**Steps**:
1. Describe modification intent
2. System performs semantic matching for Category A
3. Traverses call graph for Category B
4. Generates impact analysis report

### Phase 3: Authorization & Approval

```
Impact Report → Human Review → Scoring Authorization → Authorization Session
```

**Steps**:
1. Agent presents A/B/C classification results
2. Human provides authorization scores for critical modules
3. Creates authorization session
4. Approves for modification phase

### Phase 4: Code Modification

```
Authorization Session → AI Code Generation → Real-time Verification → Constraint Checking
```

**Steps**:
1. AI generates code within authorized scope
2. Real-time verification of WDP constraints
3. Checks FREEZE modules not modified
4. Verifies GUARD modules satisfy assertions

### Phase 5: Verification & Confirmation

```
Modification Complete → Full Verification → Audit Recording → Complete
```

**Steps**:
1. Runs full verification
2. Checks all violations resolved
3. Records AUDIT module modification notes
4. Completes the change

---

## A/B/C Classification

### Category A: Direct Impact
- **Definition**: Modules directly related to modification intent
- **Identification**:
  - Semantic matching: module ID, path, summary contain keywords
  - Role matching: Config role auto-classified on config changes
  - Direct dependency: explicitly specified by user intent
- **Treatment**: Requires重点 review, may need high authorization level

### Category B: Indirect Impact
- **Definition**: Modules related via call graph
- **Identification**:
  - Callers: modules calling Category A
  - Called: modules called by Category A
  - Propagation depth: default 2 layers
- **Treatment**: Needs attention, but authorization level can be lower

### Category C: Default Locked
- **Definition**: All other unrelated modules
- **Treatment**: Default locked as read-only, prevents accidental changes

---

## Authorization Scoring

| Score | Level | Permission | Use Case |
|-------|-------|------------|----------|
| 1 | Read-Only | No modification | FREEZE modules, Category C |
| 2 | Guarded | Restricted changes | GUARD modules, important Category B |
| 3 | Full Access | Complete modification | AUDIT/NONE modules, safe Category A |

---

## Emergency Override

### Use Cases
- Production emergency bug fixes
- Security vulnerability emergency response
- Other special situations

### Approval Levels

#### Single Approval
- **Requires**: 1 approver
- **Use**: Standard emergencies

#### Dual Approval
- **Requires**: 2 different approvers
- **Use**: High-impact changes

#### Admin Approval
- **Requires**: Admin approval
- **Use**: Highest security situations

### Workflow

1. **Create Request**
   ```bash
   watchdog override --user-id alice --email alice@company.com \
     --scope-type directory --pattern src/payment/ \
     --reason "Emergency payment bug fix" --level dual
   ```

2. **Approval Process**
   - Single: one person approval
   - Dual: two different people
   - Admin: admin only

3. **Execute Unlock**
   - Temporary access after approval
   - Time-bound (default 24 hours)
   - Usage-limited (default 1 time)

4. **Audit Record**
   - All actions recorded
   - Full approval history traceable

---

## Manifest Management

### Manifest Files

#### manifest.md
Human-readable markdown inventory

```markdown
# WATCHDOG Manifest

**Project:** my-project
**Last Sync:** 2024-03-29 17:00:00
**Total Modules:** 42

## Core Function Registry

| ID | File Location | Line | Role | Guard | Hash |
|----|---------------|------|------|-------|------|
| `payment-core` | `src/payment.js` | `10-50` | Core | FREEZE | `abc123def` |
```

#### index.json
Machine-readable JSON index

```json
{
  "project_root": "/path/to/project",
  "last_sync": "2024-03-29T17:00:00Z",
  "index_hash": "abc123def456",
  "total_modules": 42,
  "functions": {
    "payment-core": {
      "module_id": "payment-core",
      "role": "Core",
      "guard": "FREEZE",
      "file": "src/payment.js",
      "line_start": 10,
      "line_end": 50,
      "content_hash": "abc123def"
    }
  }
}
```

#### overrides.json
Emergency override records

---

## Drift Detection

### What is Drift?
Detection of discrepancies between code and index

### Detection Checks
- **New modules**: Modules added without `@wd` markers
- **Removed modules**: Modules deleted but still in index
- **Modified hashes**: Content hash changed unexpectedly
- **Line changes**: Line numbers shifted

### Drift Response
```python
drift = manifest_manager.check_drift()
if drift["has_drift"]:
    print("Drift detected!")
    print("New modules:", drift["new_modules"])
    print("Removed modules:", drift["removed_modules"])
    print("Modified hashes:", drift["modified_hashes"])
```

### Reindexing
```python
count = manifest_manager.reindex()
print(f"Reindexed {count} modules")
```

---

## Audit Trail

All actions are recorded:
- Authorization sessions
- Approval decisions
- Emergency overrides
- Drift detection events
- Reindex operations

---

*WGW v1.1 Protocol Specification
