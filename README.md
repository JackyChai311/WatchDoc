# 🛰️ WATCHDOC(watchdog for code)

> AI-Native Code Governance Protocol System

[![GitHub Stars](https://img.shields.io/github/stars/JackyChai311/WatchDoc?style=social)](https://github.com/JackyChai311/WatchDoc)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![CI Status](https://github.com/JackyChai311/WatchDoc/actions/workflows/ci.yml/badge.svg)](https://github.com/JackyChai311/WatchDoc/actions)

**WATCHDOC** is an AI-native code governance protocol system. It provides "self-protecting" capabilities through the WDP inline protocol, assigning an independent "watchdog" to each module. This prevents AI from "over-smart" refactoring and "amnesiac" modifications after context compression, achieving a paradigm shift from "blind luck" to "precise control" in code changes.

---

## ✨ Features

### 🔒 WDP Protocol (Watchdog Description Protocol)
- **Inline protection markers** - Embed protection rules directly in code comments
- **Multi-language support** - Python, JavaScript, TypeScript, Java, Go, Rust, C/C++
- **Three-level compression** - L0_FULL, L1_NAV, L2_META for context-aware usage

### 🐕 Independent Watchdogs
- **Module-level granularity** - Each function/module has its own protection
- **Four guard levels** - FREEZE, GUARD, AUDIT, NONE
- **Assertion rules** - Signature_Lock, Complexity_Limit, Test_Linked, and more

### 🎯 Precise Control
- **A/B/C classification** - Smart impact analysis based on user intent
- **1/2/3 authorization scoring** - Read-only, Guarded, Full Access
- **Human-in-the-Loop** - Human decision-making for critical modules

### 🚨 Emergency Override
- **Three-level approval** - Single, Dual, Admin
- **Time-bound access** - Configurable duration (default 24 hours)
- **Usage limits** - Prevent abuse of emergency privileges

---

## 🚀 Quick Start

### Installation

```bash
# From source
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc
pip install -e .
```

### Three-Minute Tutorial

```python
import watchdog

# 1. Initialize your project
result = watchdog.init("/path/to/your/project")
print(f"Indexed {result['modules_indexed']} modules")

# 2. Create an authorization session
session = watchdog.create_session(
    intent="Modify payment timeout logic",
    user_id="alice",
    project_path="/path/to/your/project"
)

# 3. Get impact analysis
impact = watchdog.analyze(session.session_id, "/path/to/your/project")
print(f"Category A (direct impact): {len(impact['category_a'])} modules")
print(f"Category B (indirect impact): {len(impact['category_b'])} modules")

# 4. Authorize specific functions
watchdog.authorize(session.session_id, "payment_timeout_handler", 2, "/path/to/your/project")

# 5. Verify code changes
result = watchdog.verify(session.session_id, "modified_code.py", "/path/to/your/project")
if result.ok:
    print("✅ Verification passed!")
else:
    print("❌ Violations found:", result.violations)
```

### CLI Usage

```bash
# Initialize project
watchdog init /path/to/your/project

# Scan impact
watchdog scan /path/to/your/project --intent "Modify payment logic"

# Create override request
watchdog override --user-id alice --email alice@company.com \
  --scope-type directory --pattern src/payment/ \
  --reason "Emergency payment bug fix" --level dual

# Approve override request
watchdog approve --request-id OVR-20240329-0001 \
  --user-id bob --email bob@company.com \
  --decision approve

# Verify code changes
watchdog verify /path/to/your/project modified_code.py
```

---

## 📖 How It Works

### WDP Marker Syntax

```javascript
// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic - DO NOT MODIFY"
// @wd-assert: Signature_Lock
// @wd-assert: Test_Linked: test-file:tests/payment.test.js
function processPayment(amount, cardInfo) {
    // Core payment logic here
    // AI sees the @wd: FREEZE marker and knows: DON'T TOUCH THIS!
}
// @wd: payment-core | END
```

### Guard Levels

| Level | Description | Modification Allowed |
|-------|-------------|---------------------|
| **FREEZE** | Core assets, frozen | ❌ No modification |
| **GUARD** | Critical logic, contract protected | ⚠️ Restricted, must satisfy assertions |
| **AUDIT** | Normal logic, change tracking | ✅ Allowed, but requires note |
| **NONE** | Navigation only | ✅ Full access |

### Authorization Scores

| Score | Level | Permission |
|-------|-------|------------|
| 1 | Read-Only | No modification |
| 2 | Guarded | Restricted changes |
| 3 | Full Access | Complete freedom |

---

## 🌐 Architecture

```
watchdog/
├── wdp/          # Watchdog Description Protocol
│   ├── parser.py      # Marker parser
│   └── verifier.py    # Code verifier
├── wgw/          # Watchdog Gateway
│   ├── manifest.py     # Manifest management
│   ├── authorization.py # Authorization system
│   └── override.py     # Emergency override
├── index/        # Impact analysis
│   └── analyzer.py     # A/B/C classification
├── api.py        # Unified Python API
├── cli/          # Command-line interface
│   └── main.py
└── __init__.py
```

---

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JackyChai311/WatchDoc.git
cd WatchDoc

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 src/
```

---

## 📚 Documentation

- 📖 [Whitepaper](docs/WHITEPAPER.md) - Complete technical whitepaper
- 📖 [WDP Protocol Specification](docs/WDP.md) - Marker protocol reference
- 📖 [WGW Governance Protocol](docs/WGW.md) - Governance workflow
- 🚀 [Getting Started Guide](docs/GETTING_STARTED.md) - Quick start tutorial
- 💡 [API Reference](docs/API.md) - Complete API documentation

---

## 🔒 Security

If you discover a security vulnerability, please see our [Security Policy](SECURITY.md) for responsible disclosure.

---

## 📄 License

WATCHDOG is released under the [Apache 2.0 License](LICENSE).

---

## 🙏 Acknowledgments

Thanks to all our [contributors](https://github.com/JackyChai311/WatchDoc/graphs/contributors)!

---

**Give each code module its own watchdog, and make AI code modifications predictable and controllable!** 🐕

[Get Started](docs/GETTING_STARTED.md) · [Report Issues](https://github.com/JackyChai311/WatchDoc/issues) · [Discussions](https://github.com/JackyChai311/WatchDoc/discussions)
