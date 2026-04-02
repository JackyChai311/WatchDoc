#!/usr/bin/env python3
"""
WATCHDOC Authorization System - A/B/C classifyAuthorization
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime

class FunctionCategory(Enum):
    A = "A"  # 
    B = "B"  # 
    C = "C"  # 

class AuthorizationScore(Enum):
    READ_ONLY = 1      # 
    GUARDED = 2        # 
    FULL_ACCESS = 3    # 

@dataclass
class FunctionAuthorization:
    function_id: str
    category: FunctionCategory
    score: AuthorizationScore
    reason: str = ""
    authorized_by: str = ""
    authorized_at: str = field(default_factory=lambda: datetime.now().isoformat())
 
    def to_dict(self) -> Dict:
        return {
            "function_id": self.function_id,
            "category": self.category.value,
            "score": self.score.value,
            "reason": self.reason,
            "authorized_by": self.authorized_by,
            "authorized_at": self.authorized_at
        }

@dataclass
class AuthorizationSession:
    session_id: str
    user_intent: str
    created_at: str
    authorizations: Dict[str, FunctionAuthorization] = field(default_factory=dict)
    status: str = "pending"  # pending, approved, executed, expired
 
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_intent": self.user_intent,
            "created_at": self.created_at,
            "authorizations": {k: v.to_dict() for k, v in self.authorizations.items()},
            "status": self.status
        }

class AuthorizationManager:
    """Manager"""
 
    def __init__(self):
        self.sessions: Dict[str, AuthorizationSession] = {}
        self.history: List[AuthorizationSession] = []
 
    def create_session(self, user_intent: str, user_id: str) -> AuthorizationSession:
        session_id = f"AUTH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session = AuthorizationSession(
            session_id=session_id,
            user_intent=user_intent,
            created_at=datetime.now().isoformat()
        )
        self.sessions[session_id] = session
        return session
 
    def authorize_function(self, session_id: str, function_id: str,
                          score: int, reason: str = "", user_id: str = "") -> bool:
        if session_id not in self.sessions:
            return False
 
        session = self.sessions[session_id]
        category = FunctionCategory.A  #  A 
 
        session.authorizations[function_id] = FunctionAuthorization(
            function_id=function_id,
            category=category,
            score=AuthorizationScore(score),
            reason=reason,
            authorized_by=user_id
        )
        return True
 
    def get_authorization(self, session_id: str, function_id: str) -> Optional[AuthorizationScore]:
        if session_id not in self.sessions:
            return None
        session = self.sessions[session_id]
        if function_id in session.authorizations:
            return session.authorizations[function_id].score
        return AuthorizationScore.READ_ONLY  # 
 
    def approve_session(self, session_id: str) -> bool:
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].status = "approved"
        self.history.append(self.sessions[session_id])
        return True
 
    def check_permission(self, function_id: str, session_id: str = None) -> AuthorizationScore:
        """"""
        if session_id and session_id in self.sessions:
            return self.get_authorization(session_id, function_id)
        return AuthorizationScore.READ_ONLY  # 
