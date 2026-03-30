#!/usr/bin/env python3
"""
WATCHDOG API - Unified Python Interface

Complete wrapper for WDP-1.1 + WGW-1.1

Usage Example:
    import watchdog
    
    # Initialize project
    watchdog.init("/path/to/project")
    
    # Create authorization session
    session = watchdog.create_session(intent="Modify payment logic", user="alice")
    
    # Get impact analysis
    impact = watchdog.analyze(session_id=session.id)
    
    # Submit authorization
    watchdog.authorize(session_id=session.id, function_id="calc_02", score=2)
    
    # Verify code
    result = watchdog.verify(session_id=session.id, new_code=generated_code)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .wdp.parser import WDPParser, WatchdogMark, GuardLevel
from .wdp.verifier import WDPVerifier, VerificationResult
from .wgw.manifest import ManifestManager
from .wgw.authorization import AuthorizationManager, AuthorizationScore
from .wgw.override import OverrideManager, OverrideScope, ApprovalLevel
from .index.analyzer import ImpactAnalyzer


@dataclass
class WatchdogSession:
    """WATCHDOG Session"""
    session_id: str
    user_intent: str
    user_id: str
    created_at: str
    authorizations: Dict[str, int] = field(default_factory=dict)
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_intent": self.user_intent,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "authorizations": self.authorizations,
            "status": self.status
        }


class WatchdogAPI:
    """
    WATCHDOG Unified API
    
    Provides a clean Python interface for managing AI code governance workflows.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.manifest_manager = ManifestManager(str(project_path))
        self.auth_manager = AuthorizationManager()
        self.override_manager = OverrideManager(
            str(project_path / ".watchdog" / "overrides.json")
        )
        self.analyzer = ImpactAnalyzer(str(project_path))
        self._sessions: Dict[str, WatchdogSession] = {}
    
    # ========== Initialization ==========
    
    def init(self) -> Dict:
        """
        Initialize project
        
        Scan @wd markers in code and generate Manifest.
        
        Returns:
            Dict: Initialization result
        """
        marks = WDPParser.parse_project(str(self.project_path))
        self.manifest_manager.sync_from_marks(marks)
        
        return {
            "ok": True,
            "modules_indexed": len(marks),
            "manifest_path": str(self.manifest_manager.manifest_path),
            "index_path": str(self.manifest_manager.index_path)
        }
    
    # ========== Session Management ==========
    
    def create_session(self, intent: str, user_id: str) -> WatchdogSession:
        """
        Create authorization session
        
        Args:
            intent: User modification intent
            user_id: User ID
        
        Returns:
            WatchdogSession: Session object
        """
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session = WatchdogSession(
            session_id=session_id,
            user_intent=intent,
            user_id=user_id,
            created_at=datetime.now().isoformat()
        )
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[WatchdogSession]:
        """Get session"""
        return self._sessions.get(session_id)
    
    def authorize(self, session_id: str, function_id: str, score: int) -> bool:
        """
        Authorize function modification
        
        Args:
            session_id: Session ID
            function_id: Function ID
            score: Authorization score (1=read-only, 2=guarded, 3=full)
        
        Returns:
            bool: Success status
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if score not in [1, 2, 3]:
            return False
        
        session.authorizations[function_id] = score
        return True
    
    # ========== Impact Analysis ==========
    
    def analyze(self, session_id: Optional[str] = None) -> Dict:
        """
        Perform impact analysis
        
        Args:
            session_id: Optional session ID
        
        Returns:
            Dict: Impact analysis result
        """
        # Index project
        self.analyzer.index_project()
        
        # Get user intent
        intent = ""
        if session_id and session_id in self._sessions:
            intent = self._sessions[session_id].user_intent
            # Auto-populate authorizations
            self._sessions[session_id].authorizations = {}
        
        # Perform analysis
        if intent:
            result = self.analyzer.analyze(intent)
        else:
            # Return all functions when no intent
            all_marks = list(self.analyzer.functions.values())
            result = {
                "session_id": session_id or f"ANALYSIS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "user_intent": intent,
                "category_a": [m.to_dict() for m in all_marks],
                "category_b": [],
                "category_c_count": 0,
                "total_functions": len(all_marks),
                "timestamp": datetime.now().isoformat()
            }
        
        # Update session authorizations
        if session_id and session_id in self._sessions:
            for mark_data in result.get("category_a", []):
                module_id = mark_data["module_id"]
                guard = GuardLevel(mark_data["guard"])
                
                # Smart pre-scoring
                if guard == GuardLevel.FREEZE:
                    score = 1
                elif guard == GuardLevel.NONE:
                    score = 3
                else:
                    score = 2
                
                self._sessions[session_id].authorizations[module_id] = score
            
            for mark_data in result.get("category_b", []):
                self._sessions[session_id].authorizations[mark_data["module_id"]] = 1
        
        return result
    
    # ========== Code Verification ==========
    
    def verify(self, session_id: str, new_code_path: str) -> VerificationResult:
        """
        Verify code changes
        
        Args:
            session_id: Session ID
            new_code_path: New code file path
        
        Returns:
            VerificationResult: Verification result
        """
        # Load original marks
        index = self.manifest_manager.load_index()
        original_marks = [
            WatchdogMark.from_dict(data) 
            for data in index.get("functions", {}).values()
        ]
        
        # Get session authorizations
        session = self._sessions.get(session_id)
        authorizations = session.authorizations if session else {}
        
        # Verify
        verifier = WDPVerifier()
        return verifier.verify(original_marks, new_code_path, authorizations)
    
    # ========== Emergency Override ==========
    
    def request_override(
        self,
        user_id: str,
        user_email: str,
        scope_type: str,
        pattern: str,
        reason: str,
        level: str = "single",
        hours: int = 24
    ) -> Dict:
        """
        Request emergency override
        
        Args:
            user_id: User ID
            user_email: User email
            scope_type: Scope type (function/module/directory)
            pattern: Match pattern
            reason: Override reason
            level: Approval level (single/dual/admin)
            hours: Expiration time in hours
        
        Returns:
            Dict: Override request info
        """
        scope = OverrideScope(type=scope_type, pattern=pattern)
        
        approval_level = {
            "single": ApprovalLevel.SINGLE,
            "dual": ApprovalLevel.DUAL,
            "admin": ApprovalLevel.ADMIN
        }.get(level, ApprovalLevel.SINGLE)
        
        request = self.override_manager.create_request(
            requester_id=user_id,
            requester_email=user_email,
            scope=scope,
            reason=reason,
            approval_level=approval_level,
            duration_hours=hours
        )
        
        return {
            "request_id": request.request_id,
            "status": request.status.value,
            "expires_at": request.expires_at
        }
    
    def approve_override(
        self,
        request_id: str,
        approver_id: str,
        approver_email: str,
        decision: str,
        comment: str = ""
    ) -> bool:
        """
        Approve emergency override request
        
        Args:
            request_id: Request ID
            approver_id: Approver ID
            approver_email: Approver email
            decision: Decision (approve/reject)
            comment: Approval comment
        
        Returns:
            bool: Success status
        """
        return self.override_manager.submit_approval(
            request_id=request_id,
            approver_id=approver_id,
            approver_email=approver_email,
            decision=decision,
            comment=comment
        )
    
    # ========== Drift Detection ==========
    
    def check_drift(self) -> Dict:
        """
        Check drift between code and index
        
        Returns:
            Dict: Drift detection result
        """
        return self.manifest_manager.check_drift()
    
    def reindex(self) -> int:
        """
        Reindex project
        
        Returns:
            int: Number of indexed modules
        """
        return self.manifest_manager.reindex()


# ========== Convenience Functions ==========

# Global API instances
_instances: Dict[str, WatchdogAPI] = {}


def init(project_path: str) -> Dict:
    """
    Initialize project
    
    Args:
        project_path: Project path
    
    Returns:
        Dict: Initialization result
    """
    api = WatchdogAPI(project_path)
    _instances[project_path] = api
    return api.init()


def create_session(intent: str, user_id: str, project_path: str) -> WatchdogSession:
    """
    Create authorization session
    
    Args:
        intent: Modification intent
        user_id: User ID
        project_path: Project path
    
    Returns:
        WatchdogSession: Session object
    """
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path].create_session(intent, user_id)


def analyze(session_id: str, project_path: str) -> Dict:
    """
    Perform impact analysis
    
    Args:
        session_id: Session ID
        project_path: Project path
    
    Returns:
        Dict: Impact analysis result
    """
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path].analyze(session_id)


def authorize(session_id: str, function_id: str, score: int, project_path: str) -> bool:
    """
    Authorize function modification
    
    Args:
        session_id: Session ID
        function_id: Function ID
        score: Authorization score
        project_path: Project path
    
    Returns:
        bool: Success status
    """
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path].authorize(session_id, function_id, score)


def verify(session_id: str, new_code_path: str, project_path: str) -> VerificationResult:
    """
    Verify code changes
    
    Args:
        session_id: Session ID
        new_code_path: New code file path
        project_path: Project path
    
    Returns:
        VerificationResult: Verification result
    """
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path].verify(session_id, new_code_path)


def request_override(
    user_id: str,
    user_email: str,
    scope_type: str,
    pattern: str,
    reason: str,
    project_path: str,
    level: str = "single",
    hours: int = 24
) -> Dict:
    """
    Request emergency override
    
    Args:
        user_id: User ID
        user_email: User email
        scope_type: Scope type
        pattern: Match pattern
        reason: Override reason
        project_path: Project path
        level: Approval level
        hours: Expiration time
    
    Returns:
        Dict: Override request info
    """
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path].request_override(
        user_id, user_email, scope_type, pattern, reason, level, hours
    )


def get_api(project_path: str) -> WatchdogAPI:
    """Get project API instance"""
    if project_path not in _instances:
        init(project_path)
    return _instances[project_path]
