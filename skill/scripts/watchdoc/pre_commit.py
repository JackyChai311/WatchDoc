#!/usr/bin/env python3
"""
WatchDoc Pre-commit Verification Hook
Verifies that code changes comply with WDP protection rules.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchdoc.wdp.parser import WDPParser, WatchdocMark, GuardLevel


class PreCommitVerifier:
    """Pre-commit verification for WDP compliance."""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.violations = []
        self.warnings = []
        self.authorized_modules = set()
        
    def get_staged_files(self) -> List[str]:
        """Get list of staged files from git."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f and self._is_supported_file(f)]
        except subprocess.CalledProcessError:
            return []
    
    def _is_supported_file(self, filepath: str) -> bool:
        """Check if file is supported by WDP."""
        supported_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
            '.c', '.cpp', '.h', '.hpp', '.cs', '.swift', '.kt', '.kts',
            '.scala', '.rb', '.php', '.sh', '.lua', '.pl', '.r'
        }
        return Path(filepath).suffix.lower() in supported_extensions
    
    def load_authorizations(self) -> Set[str]:
        """Load currently authorized modules from temporary grants."""
        grants_file = self.repo_root / '.watchdoc' / 'temporary_grants.json'
        if grants_file.exists():
            try:
                with open(grants_file, 'r') as f:
                    data = json.load(f)
                    if data.get('status') == 'active':
                        return {g['module_id'] for g in data.get('grants', [])}
            except (json.JSONDecodeError, IOError):
                pass
        return set()
    
    def get_file_content_at_head(self, filepath: str) -> str:
        """Get file content from HEAD (before staging)."""
        try:
            result = subprocess.run(
                ['git', 'show', f'HEAD:{filepath}'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def get_staged_content(self, filepath: str) -> str:
        """Get staged file content."""
        staged_path = self.repo_root / filepath
        if staged_path.exists():
            return staged_path.read_text(encoding='utf-8', errors='ignore')
        return ""
    
    def verify_file(self, filepath: str) -> Tuple[bool, List[str], List[str]]:
        """
        Verify a single file for WDP compliance.
        Returns: (passed, violations, warnings)
        """
        violations = []
        warnings = []
        
        # Get before and after content
        before_content = self.get_file_content_at_head(filepath)
        after_content = self.get_staged_content(filepath)
        
        # If file is new, no WDP markers to check
        if not before_content:
            return True, [], []
        
        # Parse WDP markers from original file
        try:
            original_marks = WDPParser.parse_file(str(self.repo_root / filepath))
        except Exception as e:
            warnings.append(f"Could not parse WDP markers in {filepath}: {e}")
            return True, [], warnings
        
        # Check each protected module
        for mark in original_marks:
            if mark.guard == GuardLevel.FREEZE:
                # Check if module still exists
                after_lines = after_content.split('\n')
                module_found = False
                
                for i, line in enumerate(after_lines):
                    if f'@wd: {mark.module_id}' in line:
                        module_found = True
                        break
                
                if not module_found:
                    violations.append(
                        f"🔒 FREEZE module '{mark.module_id}' was deleted or modified in {filepath}"
                    )
                    continue
                
                # Check if module is authorized
                if mark.module_id in self.authorized_modules:
                    warnings.append(
                        f"✓ FREEZE module '{mark.module_id}' modification is authorized"
                    )
                    continue
                
                # Check if content hash changed (indicates modification)
                after_marks = WDPParser.parse_file(str(self.repo_root / filepath))
                after_mark = next((m for m in after_marks if m.module_id == mark.module_id), None)
                
                if after_mark and after_mark.content_hash != mark.content_hash:
                    violations.append(
                        f"🔒 FREEZE module '{mark.module_id}' was modified without authorization in {filepath}"
                    )
            
            elif mark.guard == GuardLevel.GUARD:
                # Check assertions
                after_marks = WDPParser.parse_file(str(self.repo_root / filepath))
                after_mark = next((m for m in after_marks if m.module_id == mark.module_id), None)
                
                if after_mark:
                    for rule in mark.asserts:
                        if rule.rule_type == "Signature_Lock":
                            if mark.entry != after_mark.entry:
                                violations.append(
                                    f"⚠️ GUARD module '{mark.module_id}' signature changed in {filepath}"
                                )
            
            elif mark.guard == GuardLevel.AUDIT:
                # Check if modification has note
                after_marks = WDPParser.parse_file(str(self.repo_root / filepath))
                after_mark = next((m for m in after_marks if m.module_id == mark.module_id), None)
                
                if after_mark and after_mark.content_hash != mark.content_hash:
                    # Check for @wd-note
                    has_note = any('@wd-note:' in line for line in after_mark.raw_lines)
                    if not has_note:
                        warnings.append(
                            f"📝 AUDIT module '{mark.module_id}' modified without @wd-note in {filepath}"
                        )
        
        passed = len(violations) == 0
        return passed, violations, warnings
    
    def verify_all(self) -> bool:
        """Verify all staged files."""
        self.authorized_modules = self.load_authorizations()
        
        staged_files = self.get_staged_files()
        if not staged_files:
            return True
        
        all_passed = True
        
        for filepath in staged_files:
            passed, violations, warnings = self.verify_file(filepath)
            self.violations.extend(violations)
            self.warnings.extend(warnings)
            if not passed:
                all_passed = False
        
        return all_passed
    
    def print_report(self):
        """Print verification report."""
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.violations:
            print("\n❌ WDP VIOLATIONS DETECTED:")
            for violation in self.violations:
                print(f"   {violation}")
            print("\n   To modify FREEZE modules:")
            print("   1. Run: watchdoc grant /path/to/project --module-id=<name> --level=AUDIT --reason=\"<reason>\"")
            print("   2. Re-commit your changes")
        else:
            print("\n✅ WDP verification passed!")


def main():
    """Main entry point for pre-commit hook."""
    # Get repository root
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=True
    )
    repo_root = result.stdout.strip()
    
    verifier = PreCommitVerifier(repo_root)
    passed = verifier.verify_all()
    verifier.print_report()
    
    if not passed:
        print("\n🚫 Commit blocked due to WDP violations.")
        print("   Grant temporary authorization or revert changes.\n")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
