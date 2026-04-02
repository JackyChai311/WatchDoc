#!/usr/bin/env python3
"""
Temporary Grant Manager

Manages temporary authorization for FREEZE functions with authorization reclamation mechanism.
"""

import yaml
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TemporaryGrant:
    """Temporary authorization record"""
    module_id: str                  # Function module ID
    original_guard: str             # Original protection level (usually FREEZE)
    granted_guard: str              # Granted temporary level (GUARD/AUDIT)
    grant_reason: str               # Authorization reason
    grant_time: str                 # Authorization time
    session_id: str                 # Session ID
    topic: str                      # Modification topic
    expires_at: str                 # Expiration time


@dataclass
class ModificationSession:
    """Modification session"""
    session_id: str                 # Unique session ID
    topic: str                      # Modification topic
    started_at: str                 # Start time
    last_activity: str              # Last activity time
    granted_modules: List[str]      # List of authorized modules
    status: str = "active"          # active / completed


class TemporaryGrantManager:
    """Temporary Grant Manager"""
    
    DEFAULT_EXPIRY_MINUTES = 30     # Default authorization validity (minutes)
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.watchdoc_dir = self.project_root / '.watchdoc'
        self.grants_file = self.watchdoc_dir / 'temporary_grants.yaml'
        self.session_file = self.watchdoc_dir / 'current_session.yaml'
        
        # Ensure directory exists
        self.watchdoc_dir.mkdir(exist_ok=True)
    
    def create_session(self, topic: str) -> ModificationSession:
        """Create new modification session"""
        session = ModificationSession(
            session_id=str(uuid.uuid4())[:8],
            topic=topic,
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            granted_modules=[]
        )
        
        self._save_session(session)
        return session
    
    def get_current_session(self) -> Optional[ModificationSession]:
        """Get current active session"""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    return ModificationSession(**data)
        except:
            pass
        return None
    
    def update_session_activity(self, session: ModificationSession):
        """Update session activity time"""
        session.last_activity = datetime.now().isoformat()
        self._save_session(session)
    
    def complete_session(self, session: ModificationSession):
        """Complete session"""
        session.status = "completed"
        self._save_session(session)
    
    def request_grant(
        self,
        module_id: str,
        original_guard: str,
        requested_guard: str,
        reason: str,
        topic: str,
        expiry_minutes: int = None
    ) -> TemporaryGrant:
        """
        Request temporary authorization
        
        Args:
            module_id: Function module ID
            original_guard: Original protection level
            requested_guard: Requested temporary level
            reason: Authorization reason
            topic: Modification topic
            expiry_minutes: Validity period (minutes)
        
        Returns:
            TemporaryGrant: Temporary authorization record
        """
        # Get or create session
        session = self.get_current_session()
        if not session or session.topic != topic:
            # New topic, create new session
            session = self.create_session(topic)
        
        # Set expiration time
        expiry_minutes = expiry_minutes or self.DEFAULT_EXPIRY_MINUTES
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        
        # Create authorization record
        grant = TemporaryGrant(
            module_id=module_id,
            original_guard=original_guard,
            granted_guard=requested_guard,
            grant_reason=reason,
            grant_time=datetime.now().isoformat(),
            session_id=session.session_id,
            topic=topic,
            expires_at=expires_at.isoformat()
        )
        
        # Save authorization
        self._save_grant(grant)
        
        # Update session
        if module_id not in session.granted_modules:
            session.granted_modules.append(module_id)
        self.update_session_activity(session)
        
        return grant
    
    def get_grant(self, module_id: str) -> Optional[TemporaryGrant]:
        """Get current temporary authorization for function"""
        grants = self._load_all_grants()
        
        if module_id not in grants:
            return None
        
        grant_data = grants[module_id]
        grant = TemporaryGrant(**grant_data)
        
        # Check if expired
        if datetime.fromisoformat(grant.expires_at) < datetime.now():
            # Authorization expired, automatically revoke
            self.revoke_grant(module_id)
            return None
        
        return grant
    
    def revoke_grant(self, module_id: str) -> bool:
        """
        Revoke single temporary authorization
        
        Returns:
            bool: Whether successfully revoked
        """
        grants = self._load_all_grants()
        
        if module_id not in grants:
            return False
        
        # Record original protection level
        original_guard = grants[module_id]['original_guard']
        
        # Delete authorization record
        del grants[module_id]
        
        # Save
        self._save_all_grants(grants)
        
        return True
    
    def revoke_all_grants(self, session_id: str = None) -> List[str]:
        """
        Revoke all temporary authorizations
        
        Args:
            session_id: Specify session ID, if None revoke all
        
        Returns:
            List[str]: List of revoked module IDs
        """
        grants = self._load_all_grants()
        revoked = []
        
        modules_to_revoke = []
        if session_id:
            # Only revoke authorizations for specified session
            modules_to_revoke = [
                mid for mid, g in grants.items()
                if g.get('session_id') == session_id
            ]
        else:
            # Revoke all
            modules_to_revoke = list(grants.keys())
        
        for module_id in modules_to_revoke:
            del grants[module_id]
            revoked.append(module_id)
        
        self._save_all_grants(grants)
        return revoked
    
    def list_active_grants(self) -> List[TemporaryGrant]:
        """List all active temporary authorizations"""
        grants = self._load_all_grants()
        active = []
        
        for module_id, grant_data in grants.items():
            grant = TemporaryGrant(**grant_data)
            
            # Check if expired
            if datetime.fromisoformat(grant.expires_at) < datetime.now():
                # Authorization expired, automatically revoke
                self.revoke_grant(module_id)
                continue
            
            active.append(grant)
        
        return active
    
    def _save_grant(self, grant: TemporaryGrant):
        """Save single authorization"""
        grants = self._load_all_grants()
        grants[grant.module_id] = asdict(grant)
        self._save_all_grants(grants)
    
    def _load_all_grants(self) -> Dict:
        """Load all authorizations"""
        if not self.grants_file.exists():
            return {}
        
        try:
            with open(self.grants_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _save_all_grants(self, grants: Dict):
        """Save all authorizations"""
        with open(self.grants_file, 'w', encoding='utf-8') as f:
            yaml.dump(grants, f, default_flow_style=False, allow_unicode=True)
    
    def _save_session(self, session: ModificationSession):
        """Save session"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(session), f, default_flow_style=False, allow_unicode=True)
    
    def generate_grant_request_report(self, modules: List[Dict], topic: str) -> str:
        """
        Generate human-readable temporary authorization request report
        
        Args:
            modules: List of modules needing authorization, each containing:
                     - module_id: Module ID
                     - file_path: File path
                     - line_start: Start line
                     - line_end: End line
                     - summary: Function summary
                     - current_guard: Current protection level
                     - recommended_guard: Recommended authorization level
            topic: Modification topic
        
        Returns:
            str: Formatted report
        """
        report = []
        report.append("=" * 70)
        report.append("📋 Temporary Authorization Request")
        report.append("=" * 70)
        report.append(f"\n📌 Modification Topic: {topic}\n")
        report.append("The following functions are currently FREEZE (completely frozen) and require your temporary authorization to modify:\n")
        
        for i, module in enumerate(modules, 1):
            report.append("━" * 70)
            report.append(f"\n{i}. 🔒 {module['module_id']}")
            report.append(f"   ├─ Function: {module.get('summary', 'No description')}")
            report.append(f"   ├─ Location: {module['file_path']} (Lines {module['line_start']}-{module['line_end']})")
            report.append(f"   └─ Current level: {module['current_guard']}")
            report.append(f"\n   💡 Recommended authorization: {module.get('recommended_guard', 'AUDIT')}")
            report.append(f"\n   Please select authorization level:")
            report.append(f"   [ ] AUDIT  - Allow modification, record audit log (Recommended)")
            report.append(f"   [ ] GUARD  - Allow modification, warn before modification")
            report.append(f"   [ ] NONE   - Allow free modification (Not recommended)")
            report.append(f"   [ ] Skip   - Do not authorize this function, keep FREEZE")
        
        report.append("\n" + "━" * 70)
        report.append("\n📊 Authorization Level Description:")
        report.append("• AUDIT: Allow modification, all operations recorded to audit log")
        report.append("• GUARD: Allow modification, warning prompt before modification")
        report.append("• NONE:  Allow free modification, no restrictions (higher risk)")
        report.append(f"\n⏰ Validity Period: Default {self.DEFAULT_EXPIRY_MINUTES} minutes, automatically reclaims after timeout")
        report.append("🔄 Topic Switch: If you switch to a new topic, authorization will be automatically reclaimed")
        report.append("\n" + "=" * 70)
        report.append("\n❓ Please select authorization level individually, or choose batch authorization:")
        report.append("   1. Individual authorization: Select level for each function separately")
        report.append("   2. Batch authorization: Grant AUDIT to all (Recommended)")
        report.append("   3. Batch authorization: Grant GUARD to all")
        report.append("   4. Deny authorization: Keep all functions as FREEZE")
        report.append("=" * 70)
        
        return "\n".join(report)


# CLI Command Handlers
def cmd_grant(args):
    """CLI command: Grant temporary authorization"""
    manager = TemporaryGrantManager(args.project)
    
    grant = manager.request_grant(
        module_id=args.module_id,
        original_guard="FREEZE",  # Usually FREEZE
        requested_guard=args.level,
        reason=args.reason,
        topic=args.topic or args.reason
    )
    
    print(f"✅ Temporary authorization granted")
    print(f"   Module: {grant.module_id}")
    print(f"   Original level: {grant.original_guard}")
    print(f"   Temporary level: {grant.granted_guard}")
    print(f"   Expires at: {grant.expires_at}")


def cmd_revoke(args):
    """CLI command: Revoke temporary authorization"""
    manager = TemporaryGrantManager(args.project)
    
    if args.module_id:
        # Revoke single module
        success = manager.revoke_grant(args.module_id)
        if success:
            print(f"✅ Authorization revoked: {args.module_id}")
        else:
            print(f"⚠️  No active authorization found: {args.module_id}")
    else:
        # Revoke all
        revoked = manager.revoke_all_grants()
        if revoked:
            print(f"✅ All authorizations revoked: {len(revoked)} modules")
            for mid in revoked:
                print(f"   - {mid}")
        else:
            print("⚠️  No active authorizations found")


def cmd_session_status(args):
    """CLI command: View session status"""
    manager = TemporaryGrantManager(args.project)
    
    session = manager.get_current_session()
    grants = manager.list_active_grants()
    
    print("=" * 60)
    print("📊 Current Session Status")
    print("=" * 60)
    
    if session:
        print(f"Session ID: {session.session_id}")
        print(f"Topic: {session.topic}")
        print(f"Started at: {session.started_at}")
        print(f"Last activity: {session.last_activity}")
        print(f"Status: {session.status}")
        print(f"Authorized modules: {len(session.granted_modules)}")
        
        if grants:
            print("\nAuthorized functions:")
            for grant in grants:
                print(f"  - {grant.module_id}")
                print(f"    Level: {grant.original_guard} → {grant.granted_guard}")
                print(f"    Expires: {grant.expires_at}")
    else:
        print("No active session")
    
    print("=" * 60)
