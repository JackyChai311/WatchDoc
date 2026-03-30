# WATCHDOG API Reference

## Table of Contents
- [Quick Start](#quick-start)
- [Core API](#core-api)
- [WDP Layer](#wdp-layer)
- [WGW Layer](#wgw-layer)
- [Index Layer](#index-layer)
- [CLI Usage](#cli-usage)

---

## Quick Start

```python
import watchdog

# Initialize project
result = watchdog.init("/path/to/your/project")
print(f"Indexed {result['modules_indexed']} modules")

# Create authorization session
session = watchdog.create_session(
    intent="Modify payment timeout logic",
    user_id="alice",
    project_path="/path/to/your/project"
)

# Get impact analysis
impact = watchdog.analyze(session.session_id, "/path/to/your/project")

# Authorize specific functions
watchdog.authorize(session.session_id, "payment_timeout_handler", 2, "/path/to/your/project")

# Verify code changes
result = watchdog.verify(session.session_id, "modified_code.py", "/path/to/your/project")
```

---

## Core API

### init(project_path: str) -> Dict
Initialize a project, scan for `@wd` markers, and generate Manifest.

**Parameters**:
- `project_path`: Path to your project

**Returns**:
```python
{
    "ok": True,
    "modules_indexed": 42,
    "manifest_path": "/path/to/.watchdog/manifest.md",
    "index_path": "/path/to/.watchdog/index.json"
}
```

### create_session(intent: str, user_id: str, project_path: str) -> WatchdogSession
Create an authorization session.

**Parameters**:
- `intent`: User modification intent
- `user_id`: User ID
- `project_path`: Project path

**Returns**:
```python
WatchdogSession(
    session_id="SESSION-20240329170000",
    user_intent="Modify payment logic",
    user_id="alice",
    created_at="2024-03-29T17:00:00Z",
    authorizations={},
    status="pending"
)
```

### analyze(session_id: str, project_path: str) -> Dict
Perform impact analysis.

**Parameters**:
- `session_id`: Session ID
- `project_path`: Project path

**Returns**:
```python
{
    "session_id": "ANALYSIS-20240329170000",
    "user_intent": "Modify payment logic",
    "category_a": [...],  # Direct impact modules
    "category_b": [...],  # Indirect impact modules
    "category_c_count": 15,
    "total_functions": 42,
    "timestamp": "2024-03-29T17:00:00Z"
}
```

### authorize(session_id: str, function_id: str, score: int, project_path: str) -> bool
Authorize function modification.

**Parameters**:
- `session_id`: Session ID
- `function_id`: Function ID
- `score`: Authorization score (1=read-only, 2=guarded, 3=full)
- `project_path`: Project path

**Returns**:
- `bool`: Success status

### verify(session_id: str, new_code_path: str, project_path: str) -> VerificationResult
Verify code changes.

**Parameters**:
- `session_id`: Session ID
- `new_code_path`: New code file path
- `project_path`: Project path

**Returns**:
```python
VerificationResult(
    ok=True,
    violations=[],
    warnings=[],
    suggestions=[]
)
```

### request_override(...) -> Dict
Request emergency override.

**Parameters**:
- `user_id`: User ID
- `user_email`: User email
- `scope_type`: Scope type (function/module/directory)
- `pattern`: Match pattern
- `reason`: Override reason
- `project_path`: Project path
- `level`: Approval level (single/dual/admin)
- `hours`: Expiration time in hours

**Returns**:
```python
{
    "request_id": "OVR-20240329-0001",
    "status": "pending",
    "expires_at": "2024-03-30T17:00:00Z"
}
```

### get_api(project_path: str) -> WatchdogAPI
Get project API instance.

**Parameters**:
- `project_path`: Project path

**Returns**:
- `WatchdogAPI`: API instance

---

## WDP Layer

### WDPParser

#### parse_file(file_path: str) -> List[WatchdogMark]
Parse all WDP markers in a single file.

#### parse_project(project_root: str, extensions: List[str] = None) -> List[WatchdogMark]
Parse entire project.

### WDPVerifier

#### verify(original_marks: List[WatchdogMark], new_file_path: str, authorizations: Dict[str, int] = None) -> VerificationResult
Verify code changes against WDP constraints.

### ContextCompressor

#### compress(marks: List[WatchdogMark], level: CompressionLevel) -> str
Compress code context.

---

## WGW Layer

### ManifestManager

#### sync_from_marks(marks: List[WatchdogMark])
Sync from WDP markers to Manifest.

#### load_index() -> Dict
Load machine index.

#### get_function(module_id: str) -> Optional[WatchdogMark]
Get single function info.

#### update_function_guard(module_id: str, new_guard: GuardLevel)
Update function guard level.

#### check_drift() -> Dict
Check drift between code and index.

#### reindex() -> int
Reindex project.

### AuthorizationManager

#### create_session(user_intent: str, user_id: str) -> AuthorizationSession
Create authorization session.

#### authorize_function(session_id: str, function_id: str, score: int, reason: str = "", user_id: str = "") -> bool
Authorize function modification.

#### get_authorization(session_id: str, function_id: str) -> Optional[AuthorizationScore]
Get authorization.

### OverrideManager

#### create_request(...) -> OverrideRequest
Create override request.

#### submit_approval(...) -> bool
Submit approval.

#### check_override_permission(user_id: str, function_id: str) -> Optional[OverrideRequest]
Check override permission.

---

## Index Layer

### ImpactAnalyzer

#### index_project(extensions: List[str] = None)
Index project.

#### analyze(user_intent: str) -> Dict
Perform impact analysis.

---

## CLI Usage

### Initialize Project
```bash
watchdog init /path/to/your/project
```

### Scan Impact
```bash
watchdog scan /path/to/your/project --intent "Modify payment logic"
```

### Create Override Request
```bash
watchdog override --user-id alice --email alice@company.com \
  --scope-type directory --pattern src/payment/ \
  --reason "Emergency payment bug fix" --level dual
```

### Approve Override Request
```bash
watchdog approve --request-id OVR-20240329-0001 \
  --user-id bob --email bob@company.com \
  --decision approve
```

### Verify Code Changes
```bash
watchdog verify /path/to/your/project modified_code.py
```

---

## Data Types

### WatchdogMark
```python
@dataclass
class WatchdogMark:
    module_id: str
    role: RoleType
    guard: GuardLevel
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    entry: Optional[str] = None
    depends: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    asserts: List[AssertRule] = field(default_factory=list)
    content_hash: str = ""
    raw_lines: List[str] = field(default_factory=list)
```

### VerificationResult
```python
class VerificationResult:
    ok: bool
    violations: List[str]
    warnings: List[str]
    suggestions: List[str]
```

---

*WATCHDOG API Reference v1.1.0
