"""
WATCHDOG - AI-Native Code Governance & Protection Protocol

Complete implementation of WDP-1.1 + WGW-1.1

Official Website: https://github.com/JackyChai311/WatchDoc
Protocol Docs: https://github.com/JackyChai311/WatchDoc/blob/main/docs/WDP.md
Governance Docs: https://github.com/JackyChai311/WatchDoc/blob/main/docs/WGW.md

Core Features:
- WDP Protocol Parser: Parse @wd markers in code
- Code Verification: Verify AI-generated code against WDP constraints
- Manifest Management: Auto-maintain code protection inventory
- Authorization Scoring: A/B/C classification with 1/2/3 authorization scores
- Emergency Override: Single/Dual/Admin three-level approval
- Impact Analysis: Smart analysis of code modification impact
- Context Compression: L0_FULL / L1_NAV / L2_META three-level compression

Usage Example:
    import watchdog
    
    # Initialize project
    result = watchdog.init("/path/to/project")
    
    # Create authorization session
    session = watchdog.create_session("Modify payment logic", "alice", "/path/to/project")
    
    # Get impact analysis
    impact = watchdog.analyze(session.session_id, "/path/to/project")
    
    # Submit authorization
    watchdog.authorize(session.session_id, "calc_02", 2, "/path/to/project")
    
    # Verify code
    result = watchdog.verify(session.session_id, "new_code.py", "/path/to/project")
"""

__version__ = "1.1.0"
__author__ = "JACKY CHAI TZYY CHARNG"
__license__ = "Apache 2.0"

# WDP Layer - Protocol Definition
from .wdp import (
    WDPParser,
    WatchdogMark,
    GuardLevel,
    RoleType,
    AssertRule,
    WDPVerifier,
    VerificationResult,
    ContextCompressor
)

# WGW Layer - Governance Workflow
from .wgw import (
    ManifestManager,
    AuthorizationManager,
    AuthorizationScore,
    FunctionCategory,
    FunctionAuthorization,
    AuthorizationSession,
    OverrideManager,
    OverrideStatus,
    ApprovalLevel,
    OverrideScope
)

# Index Layer - Impact Analysis
from .index import ImpactAnalyzer

# Unified API
from .api import (
    WatchdogAPI,
    WatchdogSession,
    init,
    create_session,
    analyze,
    authorize,
    verify,
    request_override,
    get_api
)

__all__ = [
    # Version Info
    '__version__',
    '__author__',
    '__license__',
    
    # ========== WDP Layer ==========
    'WDPParser',
    'WatchdogMark',
    'GuardLevel',
    'RoleType',
    'AssertRule',
    'WDPVerifier',
    'VerificationResult',
    'ContextCompressor',
    
    # ========== WGW Layer ==========
    'ManifestManager',
    'AuthorizationManager',
    'AuthorizationScore',
    'FunctionCategory',
    'FunctionAuthorization',
    'AuthorizationSession',
    'OverrideManager',
    'OverrideStatus',
    'ApprovalLevel',
    'OverrideScope',
    
    # ========== Index Layer ==========
    'ImpactAnalyzer',
    
    # ========== Unified API ==========
    'WatchdogAPI',
    'WatchdogSession',
    'init',
    'create_session',
    'analyze',
    'authorize',
    'verify',
    'request_override',
    'get_api'
]
