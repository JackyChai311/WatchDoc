"""
WATCHDOC - AI-Native Code Governance & Security Gateway

WATCHDOC implements efficient, controllable, and compliant AI-assisted programming
through the WDP inline protocol and WGW human-in-the-loop workflow.
"""

__version__ = "1.1.0"
__author__ = "WATCHDOC Team"

from .wdp import (
    WDPParser,
    WatchdocMark,
    GuardLevel,
    RoleType,
    AssertRule,
    WDPVerifier,
    VerificationResult
)
from .wgw import (
    ManifestManager,
    AuthorizationManager,
    OverrideManager,
    FunctionCategory,
    AuthorizationScore,
    ApprovalLevel
)
from .index import ImpactAnalyzer

__all__ = [
    # WDP
    'WDPParser',
    'WatchdocMark',
    'GuardLevel',
    'RoleType',
    'AssertRule',
    'WDPVerifier',
    'VerificationResult',
    # WGW
    'ManifestManager',
    'AuthorizationManager',
    'OverrideManager',
    'FunctionCategory',
    'AuthorizationScore',
    'ApprovalLevel',
    # Index
    'ImpactAnalyzer',
]
