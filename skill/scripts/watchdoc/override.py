#!/usr/bin/env python3
"""
WATCHDOC Emergency Override - approval
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional

class OverrideStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    USED = "used"

class ApprovalLevel(Enum):
    SINGLE = "single"
    DUAL = "dual"
    ADMIN = "admin"

@dataclass
class OverrideScope:
    type: str  # function, module, directory, tag
    pattern: str
    function_ids: List[str] = field(default_factory=list)

@dataclass
class OverrideRequest:
    request_id: str
    requester_id: str
    requester_email: str
    created_at: str
    scope: OverrideScope
    reason: str
    approval_level: ApprovalLevel
    expires_at: str
    status: OverrideStatus = OverrideStatus.PENDING
    approvals: List[Dict] = field(default_factory=list)
    usage_count: int = 0
    max_usage: int = 1

class OverrideManager:
    """Manager"""
 
    def __init__(self, storage_path: str = "./.watchdoc/overrides.json"):
        self.storage_path = Path(storage_path)
        self.requests: Dict[str, OverrideRequest] = {}
        self.admin_ids: List[str] = []
        self._load()
 
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.requests = {k: self._dict_to_request(v) for k, v in data.get('requests', {}).items()}
                self.admin_ids = data.get('admin_ids', [])
 
    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'requests': {k: self._request_to_dict(v) for k, v in self.requests.items()},
            'admin_ids': self.admin_ids,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
 
    def _request_to_dict(self, req: OverrideRequest) -> Dict:
        d = asdict(req)
        d['scope'] = asdict(req.scope)
        d['approval_level'] = req.approval_level.value
        d['status'] = req.status.value
        return d
 
    def _dict_to_request(self, data: Dict) -> OverrideRequest:
        data['scope'] = OverrideScope(**data['scope'])
        data['approval_level'] = ApprovalLevel(data['approval_level'])
        data['status'] = OverrideStatus(data['status'])
        return OverrideRequest(**data)
 
    def create_request(self, requester_id: str, requester_email: str,
                      scope: OverrideScope, reason: str,
                      approval_level: ApprovalLevel = ApprovalLevel.SINGLE,
                      duration_hours: int = 24) -> OverrideRequest:
        request_id = f"OVR-{datetime.now().strftime('%Y%m%d')}-{len(self.requests)+1:04d}"
        now = datetime.now()
 
        request = OverrideRequest(
            request_id=request_id,
            requester_id=requester_id,
            requester_email=requester_email,
            created_at=now.isoformat(),
            scope=scope,
            reason=reason,
            approval_level=approval_level,
            expires_at=(now + timedelta(hours=duration_hours)).isoformat()
        )
 
        self.requests[request_id] = request
        self._save()
        return request
 
    def submit_approval(self, request_id: str, approver_id: str,
                       approver_email: str, decision: str,
                       comment: str = "") -> bool:
        if request_id not in self.requests:
            raise ValueError(f"：{request_id}")
 
        request = self.requests[request_id]
        if request.status != OverrideStatus.PENDING:
            raise ValueError(f"statusapproval：{request.status.value}")
 
        for approval in request.approvals:
            if approval['approver_id'] == approver_id:
                raise ValueError("approval")
 
        request.approvals.append({
            'approver_id': approver_id,
            'approver_email': approver_email,
            'decision': decision,
            'timestamp': datetime.now().isoformat(),
            'comment': comment
        })
 
        if self._check_approval(request):
            request.status = OverrideStatus.APPROVED
        elif decision == "reject":
            request.status = OverrideStatus.REJECTED
 
        self._save()
        return request.status == OverrideStatus.APPROVED
 
    def _check_approval(self, request: OverrideRequest) -> bool:
        approvals = [a for a in request.approvals if a['decision'] == 'approve']
        approver_ids = set(a['approver_id'] for a in approvals)
 
        if request.approval_level == ApprovalLevel.SINGLE:
            return len(approvals) >= 1
        elif request.approval_level == ApprovalLevel.DUAL:
            return len(approver_ids) >= 2 and request.requester_id not in approver_ids
        elif request.approval_level == ApprovalLevel.ADMIN:
            return any(a['approver_id'] in self.admin_ids for a in approvals)
        return False
 
    def check_override_permission(self, user_id: str, function_id: str) -> Optional[OverrideRequest]:
        for request in self.requests.values():
            if request.status != OverrideStatus.APPROVED:
                continue
            if datetime.fromisoformat(request.expires_at) < datetime.now():
                request.status = OverrideStatus.EXPIRED
                continue
            if request.usage_count >= request.max_usage:
                request.status = OverrideStatus.USED
                continue
            if self._match_scope(request.scope, function_id):
                request.usage_count += 1
                self._save()
                return request
        return None
 
    def _match_scope(self, scope: OverrideScope, function_id: str) -> bool:
        if scope.type == "function":
            return function_id in scope.function_ids
        elif scope.type == "module":
            return scope.pattern in function_id
        elif scope.type == "directory":
            return function_id.startswith(scope.pattern)
        return False
 
    def get_audit_log(self) -> List[Dict]:
        return [
            {
                'request_id': r.request_id,
                'requester': r.requester_email,
                'scope': asdict(r.scope),
                'reason': r.reason,
                'status': r.status.value,
                'created_at': r.created_at,
                'approvals': r.approvals
            }
            for r in self.requests.values()
        ]
