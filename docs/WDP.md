# WDP Protocol Specification v1.2

> Watchdoc Description Protocol

## Table of Contents
- [Overview](#overview)
- [Marker Syntax](#marker-syntax)
- [Guard Levels](#guard-levels)
- [Role Types](#role-types)
- [Assertion Rules](#assertion-rules)
- [Context Compression](#context-compression)
- [Multi-Language Support](#multi-language-support)
- [Examples](#examples)

---

## Overview

**WDP (Watchdoc Description Protocol) is an inline code protection mechanism that embeds protection rules directly in code comments. It provides "self-protecting" capabilities for AI-native code governance.

### Design Principles:
- **Inline by design: Protection rules live with the code
- **AI-readable**: Designed specifically for AI understanding
- **Context-robust**: Works even with context compression
- **Human-augmented: Preserves human intent

---

## Marker Syntax

### Basic Marker Format

```javascript
// @wd: <module-id> | <field1>: <value1> | <field2>: <value2> | ...
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `Role` | string | Module role (Core/Util/Interface/Config/Legacy) |
| `Guard` | string | Protection level (FREEZE/GUARD/AUDIT/NONE) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `Entry` | string | Entry function/class name |
| `Depends` | string[] | Dependent module IDs (comma-separated) |
| `Summary` | string | Module description |

### Marker Block

```javascript
// @wd: module-id | Role: Core | Guard: FREEZE | Summary: "Description here"
// @wd-assert: RuleType: params
... code content ...
// @wd: module-id | END
```

### End Marker

```javascript
// @wd: <module-id> | END
```

---

## Guard Levels

### FREEZE
- **Description**: Core assets, NO MODIFICATION ALLOWED
- **Use Case**: Core payment processing, authentication logic
- **Color**: Red 🔴

### GUARD
- **Description**: Critical logic, contract-protected
- **Use Case**: Important business logic with assertions
- **Color**: Yellow 🟡

### AUDIT
- **Description**: Normal logic, change tracking
- **Use Case**: Regular features, change needs note
- **Color**: Blue 🔵

### NONE
- **Description**: Navigation only, no protection
- **Use Case**: Utility functions, new features
- **Color**: Green 🟢

---

## Role Types

### Core
Core business logic, high business value

### Util
Utility functions, helpers, common libraries

### Interface
API interfaces, external-facing functions

### Config
Configuration files, settings, constants

### Legacy
Legacy code, deprecated functions

---

## Assertion Rules

### Signature_Lock
Locks function signature, prevents API changes

```javascript
// @wd-assert: Signature_Lock
```

### Complexity_Limit
Limits code complexity

```javascript
// @wd-assert: Complexity_Limit: value:10
```

### Test_Linked
Requires linked tests to pass

```javascript
// @wd-assert: Test_Linked: test-file:tests/auth.test.js
```

### Custom Assertions
Users can define custom assertion rules

---

## Context Compression

### L0_FULL
Full code + all markers
- **Use**: When token budget is sufficient
- **Preserves**: Everything

### L1_NAV
All markers + entry functions
- **Use**: When token budget is tight
- **Preserves**: Navigation capability

### L2_META
Only markers + semantic summaries
- **Use**: When token budget is extremely limited
- **Preserves**: Protection information only

---

## Multi-Language Support

### Python
```python
# @wd: module-id | Role: Core | Guard: FREEZE
```

### JavaScript/TypeScript/Java/Go/Rust/C/C++
```javascript
// @wd: module-id | Role: Core | Guard: FREEZE
```

---

## Examples

### Complete Example

```javascript
// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Depends: crypto-util, db-connector | Summary: "Core payment processing logic - DO NOT MODIFY"
// @wd-assert: Signature_Lock
// @wd-assert: Test_Linked: test-file:tests/payment.test.js
function processPayment(amount, cardInfo) {
    const hash = cryptoUtil.hashPassword(cardInfo);
    return dbConnector.verifyUser(username, hash);
}
// @wd: payment-core | END
```

### Config Module Example

```python
# @wd: app-config | Role: Config | Guard: GUARD | Summary: "Application configuration"
# @wd-assert: Signature_Lock
APP_CONFIG = {
    "debug": False,
    "max_connections": 100,
    "timeout": 30
}
# @wd: app-config | END
```

### Audit Module Example

```javascript
// @wd: feature-utils | Role: Util | Guard: AUDIT | Summary: "Feature utility functions"
function formatDate(date) {
    return date.toISOString();
}
// @wd: feature-utils | END
```

---

## File Structure

```
.watchdoc/
├── manifest.md       # Human-readable manifest
├── index.json        # Machine-readable index
└── overrides.json    # Emergency override records
```

---

*WDP v1.1 Protocol Specification
