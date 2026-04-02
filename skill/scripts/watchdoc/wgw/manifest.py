#!/usr/bin/env python3
"""
WATCHDOC Manifest Manager - WGW Governance Manifest Manager
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from ..wdp.parser import WatchdocMark, GuardLevel

class ManifestManager:
    """WATCHDOC_MANIFEST.md Manager"""
 
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.watchdoc_dir = self.project_root / ".watchdoc"
        self.manifest_path = self.watchdoc_dir / "manifest.md"
        self.index_path = self.watchdoc_dir / "index.json"
        self.watchdoc_dir.mkdir(parents=True, exist_ok=True)
 
    def sync_from_marks(self, marks: List[WatchdocMark]):
        """Sync from WDP markers to Manifest"""
        index_data = {
            "project_root": str(self.project_root),
            "last_sync": datetime.now().isoformat(),
            "total_modules": len(marks),
            "functions": {}
        }
 
        for mark in marks:
            index_data["functions"][mark.module_id] = mark.to_dict()
 
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
 
        self._update_manifest_md(marks)
 
    def _update_manifest_md(self, marks: List[WatchdocMark]):
        """Update human-readable Markdown manifest"""
        content = f"""# WATCHDOC Manifest

**Project:** {self.project_root.name}
**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Modules:** {len(marks)}

---

## Module Registry

| Module ID | File Location | Lines | Role | Guard | Description | Hash |
|-----------|---------------|-------|------|-------|-------------|------|
"""
    
        for mark in sorted(marks, key=lambda m: m.guard.value, reverse=True):
            description = mark.summary or "No description"
            content += f"| `{mark.module_id}` | `{mark.file_path}` | `{mark.line_start}-{mark.line_end}` | {mark.role.value} | {mark.guard.value} | {description} | `{mark.content_hash[:8]}` |\n"
    
        content += f"""
---

## Statistics

- **FREEZE:** {sum(1 for m in marks if m.guard == GuardLevel.FREEZE)} modules
- **GUARD:** {sum(1 for m in marks if m.guard == GuardLevel.GUARD)} modules
- **AUDIT:** {sum(1 for m in marks if m.guard == GuardLevel.AUDIT)} modules
- **NONE:** {sum(1 for m in marks if m.guard == GuardLevel.NONE)} modules

---

## Guard Level Definitions

- **FREEZE**: Core assets, NO MODIFICATION ALLOWED
- **GUARD**: Critical logic, restricted modification with assertions
- **AUDIT**: Normal logic, modification requires note
- **NONE**: No protection, free to modify

---

*This file is automatically maintained by WATCHDOC. Do not edit manually.*
"""
    
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            f.write(content)
 
    def load_index(self) -> Dict:
        """Load machine index"""
        if not self.index_path.exists():
            return {"functions": {}}
        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
 
    def get_function(self, module_id: str) -> Optional[WatchdocMark]:
        """Get single function info（considering temporary authorization）"""
        index = self.load_index()
        if module_id not in index.get("functions", {}):
            return None
        
        mark = WatchdocMark.from_dict(index["functions"][module_id])
        
        # 
        from .temporary_grant import TemporaryGrantManager
        grant_manager = TemporaryGrantManager(str(self.project_root))
        grant = grant_manager.get_grant(module_id)
        
        if grant:
            # 
            mark.guard = GuardLevel(grant.granted_guard)
        
        return mark
    
    def get_effective_guard(self, module_id: str) -> GuardLevel:
        """Protection level（considering temporary authorization）"""
        mark = self.get_function(module_id)
        if not mark:
            return GuardLevel.NONE
        return mark.guard
 
    def update_function_guard(self, module_id: str, new_guard: GuardLevel):
        """Protection level"""
        index = self.load_index()
        if module_id in index.get("functions", {}):
            index["functions"][module_id]["guard"] = new_guard.value
            index["functions"][module_id]["updated_at"] = datetime.now().isoformat()
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
    
    def check_drift(self) -> Dict:
        """"""
        from ..wdp.parser import WDPParser
        
        drift = {
            "has_drift": False,
            "new_modules": [],
            "removed_modules": [],
            "modified_hashes": [],
            "line_changes": []
        }
        
        # 
        old_index = self.load_index()
        old_functions = old_index.get("functions", {})
        
        # 
        current_marks = WDPParser.parse_project(str(self.project_root))
        current_functions = {m.module_id: m for m in current_marks}
        
        # 
        for module_id in current_functions:
            if module_id not in old_functions:
                drift["new_modules"].append(module_id)
                drift["has_drift"] = True
        
        # 
        for module_id in old_functions:
            if module_id not in current_functions:
                drift["removed_modules"].append(module_id)
                drift["has_drift"] = True
        
        # 
        for module_id, current_mark in current_functions.items():
            if module_id in old_functions:
                old_hash = old_functions[module_id].get("content_hash", "")
                if old_hash and old_hash != current_mark.content_hash:
                    drift["modified_hashes"].append({
                        "module_id": module_id,
                        "old_hash": old_hash,
                        "new_hash": current_mark.content_hash
                    })
                    drift["has_drift"] = True
                
                # 
                old_start = old_functions[module_id].get("line_start", 0)
                old_end = old_functions[module_id].get("line_end", 0)
                if old_start != current_mark.line_start or old_end != current_mark.line_end:
                    drift["line_changes"].append({
                        "module_id": module_id,
                        "old_lines": f"{old_start}-{old_end}",
                        "new_lines": f"{current_mark.line_start}-{current_mark.line_end}"
                    })
                    drift["has_drift"] = True
        
        return drift
    
    def reindex(self) -> int:
        """"""
        from ..wdp.parser import WDPParser
        
        # 
        marks = WDPParser.parse_project(str(self.project_root))
        
        #  Manifest
        self.sync_from_marks(marks)
        
        return len(marks)
    
    def list_all_functions(self) -> List[Dict]:
        """（）"""
        index = self.load_index()
        functions = []
        
        # 
        from .temporary_grant import TemporaryGrantManager
        grant_manager = TemporaryGrantManager(str(self.project_root))
        
        for module_id, func_data in index.get("functions", {}).items():
            func_info = func_data.copy()
            
            # 
            grant = grant_manager.get_grant(module_id)
            if grant:
                func_info['has_temporary_grant'] = True
                func_info['temporary_guard'] = grant.granted_guard
                func_info['grant_expires_at'] = grant.expires_at
            else:
                func_info['has_temporary_grant'] = False
            
            functions.append(func_info)
        
        return functions
    
    def list_freeze_functions(self) -> List[Dict]:
        """ FREEZE """
        all_functions = self.list_all_functions()
        return [f for f in all_functions if f['guard'] == 'FREEZE' and not f.get('has_temporary_grant')]
    
    def check_authorization_before_modify(self, module_ids: List[str], topic: str) -> Dict:
        """
        Authorization
        
        Args:
            module_ids: module ID list
            topic: topic
        
        Returns:
            Dict: Authorizationfunctionlist
        """
        from .temporary_grant import TemporaryGrantManager
        grant_manager = TemporaryGrantManager(str(self.project_root))
        
        result = {
            'need_authorization': [],
            'already_authorized': [],
            'can_modify': []
        }
        
        for module_id in module_ids:
            mark = self.get_function(module_id)
            if not mark:
                continue
            
            # 
            grant = grant_manager.get_grant(module_id)
            if grant:
                # 
                result['already_authorized'].append({
                    'module_id': module_id,
                    'granted_guard': grant.granted_guard,
                    'expires_at': grant.expires_at
                })
                result['can_modify'].append(module_id)
            elif mark.guard == GuardLevel.FREEZE:
                # 
                result['need_authorization'].append({
                    'module_id': module_id,
                    'current_guard': 'FREEZE',
                    'file_path': mark.file_path,
                    'line_start': mark.line_start,
                    'line_end': mark.line_end,
                    'summary': mark.summary
                })
            else:
                #  FREEZE，
                result['can_modify'].append(module_id)
        
        # 
        if result['need_authorization']:
            result['authorization_request'] = grant_manager.generate_grant_request_report(
                result['need_authorization'],
                topic
            )
        
        return result
