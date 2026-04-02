# WATCHDOC API Reference

## Table of Contents
- [CLI Overview](#cli-overview)
- [Initialization Commands](#initialization-commands)
- [Scanning & Analysis](#scanning--analysis)
- [Temporary Authorization](#temporary-authorization)
- [Emergency Override](#emergency-override)
- [Drift Detection](#drift-detection)
- [Python Module Reference](#python-module-reference)

---

## CLI Overview

WATCHDOC provides a command-line interface for all operations. All commands are run from the `scripts/` directory:

```bash
cd WatchDoc/scripts
python -m watchdoc.cli.main <command> [options]
```

### Global Options

```
-h, --help    Show help message and exit
```

### Available Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize project with auto-freeze |
| `scan` | Scan for impact analysis |
| `grant` | Grant temporary authorization |
| `revoke` | Revoke temporary authorization |
| `session` | View session status |
| `drift` | Detect code drift |
| `reindex` | Reindex project |
| `override` | Create override request |
| `approve` | Approve override request |

---

## Initialization Commands

### init

Initialize a project, scan all code files, and mark all functions as FREEZE.

```bash
python -m watchdoc.cli.main init <project_path> [--auto-freeze]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |
| `--auto-freeze, -a` | flag | No | Automatically mark all functions as FREEZE |

**Returns:**

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

**Generated Files:**

```
<project>/
├── .watchdoc/
│   ├── manifest.md           # Protection inventory (human-readable)
│   └── index.json            # Index file (machine-readable)
```

**Example:**

```bash
# Initialize with auto-freeze
python -m watchdoc.cli.main init /path/to/project --auto-freeze

# Initialize without auto-freeze (only scan existing @wd markers)
python -m watchdoc.cli.main init /path/to/project
```

---

## Scanning & Analysis

### scan

Perform impact analysis based on modification intent.

```bash
python -m watchdoc.cli.main scan <project_path> --intent <intent>
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |
| `--intent, -i` | string | Yes | Modification intent description |

**Returns:**

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
  ],
  "category_c_count": 15,
  "total_functions": 42
}
```

**Example:**

```bash
python -m watchdoc.cli.main scan /path/to/project --intent "Modify payment timeout logic"
```

---

## Temporary Authorization

### grant

Grant temporary authorization for FREEZE modules.

```bash
python -m watchdoc.cli.main grant <project_path> \
  --module-id <id> \
  --level <level> \
  --reason <reason> \
  [--topic <topic>]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |
| `--module-id` | string | Yes | Module ID to authorize |
| `--level` | choice | Yes | Authorization level: AUDIT, GUARD, or NONE |
| `--reason` | string | Yes | Authorization reason |
| `--topic` | string | No | Modification topic (defaults to reason) |

**Authorization Levels:**

| Level | Description | Validity |
|-------|-------------|----------|
| `AUDIT` | Allow modification, record audit log | 30 minutes |
| `GUARD` | Allow modification, warn before modification | 30 minutes |
| `NONE` | Allow free modification | 30 minutes |

**Returns:**

```
✅ Temporary authorization granted
   Module: payment_setTimeout
   Original level: FREEZE
   Temporary level: AUDIT
   Expires at: 2024-04-02T16:00:00
```

**Example:**

```bash
python -m watchdoc.cli.main grant /path/to/project \
  --module-id=payment_setTimeout \
  --level=AUDIT \
  --reason="Modify payment timeout logic"
```

### revoke

Revoke temporary authorization(s).

```bash
python -m watchdoc.cli.main revoke <project_path> [--module-id <id>]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |
| `--module-id` | string | No | Module ID to revoke (revoke all if not specified) |

**Returns:**

```
✅ All authorizations revoked: 2 modules
   - payment_setTimeout
   - payment_calculateTimeout
```

**Example:**

```bash
# Revoke all authorizations
python -m watchdoc.cli.main revoke /path/to/project

# Revoke specific module
python -m watchdoc.cli.main revoke /path/to/project --module-id=payment_setTimeout
```

### session

View current session status and active authorizations.

```bash
python -m watchdoc.cli.main session <project_path>
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |

**Returns:**

```
============================================================
📊 Current Session Status
============================================================
Session ID: a1b2c3d4
Topic: Modify payment timeout logic
Started at: 2024-04-02T15:20:00
Last activity: 2024-04-02T15:25:00
Status: active
Authorized modules: 2

Authorized functions:
  - payment_setTimeout
    Level: FREEZE → AUDIT
    Expires: 2024-04-02T15:50:00
  - payment_calculateTimeout
    Level: FREEZE → GUARD
    Expires: 2024-04-02T15:50:00
============================================================
```

**Example:**

```bash
python -m watchdoc.cli.main session /path/to/project
```

---

## Emergency Override

### override

Create an emergency override request for critical situations.

```bash
python -m watchdoc.cli.main override \
  --user-id <id> \
  --email <email> \
  --scope-type <type> \
  --pattern <pattern> \
  --reason <reason> \
  [--level <level>] \
  [--hours <hours>]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--user-id` | string | Yes | Requester user ID |
| `--email` | string | Yes | Requester email |
| `--scope-type` | choice | Yes | Scope type: function, module, or directory |
| `--pattern` | string | Yes | Match pattern |
| `--reason` | string | Yes | Override reason |
| `--level` | choice | No | Approval level: single (default), dual, or admin |
| `--hours` | int | No | Expiration time in hours (default: 24) |

**Approval Levels:**

| Level | Description | Required Approvers |
|-------|-------------|-------------------|
| `single` | Standard emergency | 1 approver |
| `dual` | High-impact changes | 2 different approvers |
| `admin` | Highest security | Admin only |

**Returns:**

```
Override request created: OVR-20240402-0001
```

**Example:**

```bash
python -m watchdoc.cli.main override \
  --user-id alice \
  --email alice@company.com \
  --scope-type directory \
  --pattern src/payment/ \
  --reason "Emergency payment bug fix" \
  --level dual
```

### approve

Approve an emergency override request.

```bash
python -m watchdoc.cli.main approve \
  --request-id <id> \
  --user-id <id> \
  --email <email> \
  --decision <decision> \
  [--comment <comment>]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--request-id` | string | Yes | Override request ID |
| `--user-id` | string | Yes | Approver user ID |
| `--email` | string | Yes | Approver email |
| `--decision` | choice | Yes | Decision: approve or reject |
| `--comment` | string | No | Optional comment |

**Returns:**

```
Approval successful
```

**Example:**

```bash
python -m watchdoc.cli.main approve \
  --request-id OVR-20240402-0001 \
  --user-id bob \
  --email bob@company.com \
  --decision approve
```

---

## Drift Detection

### drift

Detect discrepancies between code and index.

```bash
python -m watchdoc.cli.main drift <project_path>
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |

**Returns:**

```
⚠️ Drift detected!

New modules: 1
  + newModule_newFunction

Modified content: 2
  * payment_processPayment
  * auth_verifyUser

Line number changes: 1
  ~ utils_formatData: 10-20 → 10-25
```

**Drift Types:**

| Type | Description |
|------|-------------|
| New modules | Modules added without `@wd` markers |
| Removed modules | Modules deleted but still in index |
| Modified hashes | Content hash changed unexpectedly |
| Line changes | Line numbers shifted |

**Example:**

```bash
python -m watchdoc.cli.main drift /path/to/project
```

### reindex

Reindex the project after drift is detected.

```bash
python -m watchdoc.cli.main reindex <project_path>
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_path` | string | Yes | Path to the project root |

**Returns:**

```
Reindex complete: 240 modules
```

**Example:**

```bash
python -m watchdoc.cli.main reindex /path/to/project
```

---

## Python Module Reference

### Core Modules

#### watchdoc.wdp.parser

WDP marker parser.

```python
from watchdoc.wdp.parser import WDPParser, WatchdocMark, GuardLevel

# Parse a single file
marks = WDPParser.parse_file("/path/to/file.py")

# Parse entire project
marks = WDPParser.parse_project("/path/to/project")

# Access parsed data
for mark in marks:
    print(f"{mark.module_id}: {mark.guard.value}")
    print(f"  File: {mark.file_path}")
    print(f"  Lines: {mark.line_start}-{mark.line_end}")
```

#### watchdoc.wdp.auto_marker

Auto-freeze scanner.

```python
from watchdoc.wdp.auto_marker import AutoMarker
from watchdoc.wdp.parser import GuardLevel

# Create auto marker
marker = AutoMarker("/path/to/project")

# Scan and mark all functions as FREEZE
results = marker.scan_and_mark_all(default_guard=GuardLevel.FREEZE)

print(f"Files scanned: {results['total_files']}")
print(f"Functions marked: {results['total_functions']}")
```

#### watchdoc.wdp.verifier

Code change verifier.

```python
from watchdoc.wdp.verifier import WDPVerifier

# Verify code changes
result = WDPVerifier.verify(
    original_marks=marks,
    new_file_path="/path/to/modified_file.py",
    authorizations={"payment_setTimeout": 2}  # Authorization scores
)

if result.ok:
    print("✅ Verification passed!")
else:
    print("❌ Violations:", result.violations)
```

#### watchdoc.wgw.manifest

Manifest manager.

```python
from watchdoc.wgw.manifest import ManifestManager

# Create manager
manager = ManifestManager("/path/to/project")

# Sync from marks
manager.sync_from_marks(marks)

# Load index
index = manager.load_index()

# Get function info
mark = manager.get_function("payment_setTimeout")

# Update protection level
manager.update_function_guard("payment_setTimeout", GuardLevel.AUDIT)

# Check drift
drift = manager.check_drift()
if drift["has_drift"]:
    print("Drift detected!")
```

#### watchdoc.wgw.temporary_grant

Temporary authorization manager.

```python
from watchdoc.wgw.temporary_grant import TemporaryGrantManager

# Create manager
manager = TemporaryGrantManager("/path/to/project")

# Create session
session = manager.create_session("Modify payment timeout logic")

# Grant temporary authorization
grant = manager.request_grant(
    module_id="payment_setTimeout",
    original_guard="FREEZE",
    requested_guard="AUDIT",
    reason="Modify payment timeout logic",
    topic="Payment timeout optimization"
)

# Get current grant
grant = manager.get_grant("payment_setTimeout")

# List active grants
active_grants = manager.list_active_grants()

# Revoke single grant
manager.revoke_grant("payment_setTimeout")

# Revoke all grants
revoked = manager.revoke_all_grants()
```

#### watchdoc.index.analyzer

Impact analyzer.

```python
from watchdoc.index.analyzer import ImpactAnalyzer

# Create analyzer
analyzer = ImpactAnalyzer("/path/to/project")

# Index project
analyzer.index_project()

# Analyze impact
result = analyzer.analyze("Modify payment timeout logic")

print(f"Direct impact: {result['direct_impact']}")
print(f"Related modules: {result['related_modules']}")
```

---

## Data Structures

### WatchdocMark

```python
@dataclass
class WatchdocMark:
    module_id: str           # Unique module identifier
    role: RoleType           # Core, Util, Interface, Config, Legacy
    guard: GuardLevel        # FREEZE, GUARD, AUDIT, NONE
    file_path: str           # File location
    line_start: int          # Start line number
    line_end: int            # End line number
    entry: Optional[str]     # Entry function/class name
    depends: List[str]       # Dependent module IDs
    summary: Optional[str]   # Module description
    asserts: List[AssertRule] # Assertion rules
    content_hash: str        # Content hash for drift detection
```

### GuardLevel

```python
class GuardLevel(Enum):
    FREEZE = "FREEZE"  # No modification allowed
    GUARD = "GUARD"    # Restricted modification
    AUDIT = "AUDIT"    # Tracked modification
    NONE = "NONE"      # Free modification
```

### RoleType

```python
class RoleType(Enum):
    CORE = "Core"           # Core business logic
    UTIL = "Util"           # Utility functions
    INTERFACE = "Interface" # API interfaces
    CONFIG = "Config"       # Configuration files
    LEGACY = "Legacy"       # Legacy code
```

### TemporaryGrant

```python
@dataclass
class TemporaryGrant:
    module_id: str          # Module ID
    original_guard: str     # Original protection level
    granted_guard: str      # Granted temporary level
    grant_reason: str       # Authorization reason
    grant_time: str         # Authorization timestamp
    session_id: str         # Session ID
    topic: str              # Modification topic
    expires_at: str         # Expiration timestamp
```

### ModificationSession

```python
@dataclass
class ModificationSession:
    session_id: str             # Unique session ID
    topic: str                  # Modification topic
    started_at: str             # Start timestamp
    last_activity: str          # Last activity timestamp
    granted_modules: List[str]  # Authorized module IDs
    status: str                 # active or completed
```

---

## File Structure

### Generated Files

```
<project>/
├── .watchdoc/
│   ├── manifest.md            # Protection inventory (human-readable)
│   ├── index.json             # Index file (machine-readable)
│   ├── temporary_grants.yaml  # Temporary authorization records
│   ├── current_session.yaml   # Current session info
│   └── overrides.json         # Emergency override records
```

### manifest.md Format

```markdown
# WATCHDOC Manifest

**Project:** my-project
**Last Sync:** 2024-04-02 15:30:00
**Total Modules:** 237

## Module Registry

| Module ID | File Location | Lines | Role | Guard | Description | Hash |
|-----------|---------------|-------|------|-------|-------------|------|
| `payment_processPayment` | `payment.py` | `10-50` | Core | FREEZE | Core payment logic | `abc123` |

## Statistics

- **FREEZE:** 150 modules
- **GUARD:** 50 modules
- **AUDIT:** 30 modules
- **NONE:** 7 modules
```

### index.json Format

```json
{
  "project_root": "/path/to/project",
  "last_sync": "2024-04-02T15:30:00Z",
  "total_modules": 237,
  "functions": {
    "payment_processPayment": {
      "module_id": "payment_processPayment",
      "role": "Core",
      "guard": "FREEZE",
      "file": "payment.py",
      "line_start": 10,
      "line_end": 50,
      "content_hash": "abc123def"
    }
  }
}
```

---

*WATCHDOC API Reference v1.2.0
