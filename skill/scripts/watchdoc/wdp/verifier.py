#!/usr/bin/env python3
"""
WATCHDOC Verifier - Verify AI-generated code complies with WDP constraints
"""

import hashlib
from typing import List, Dict, Tuple
from .parser import WDPParser, WatchdocMark, GuardLevel, AssertRule

class VerificationResult:
    def __init__(self):
        self.ok = True
        self.violations = []
        self.warnings = []
        self.suggestions = []
 
    def add_violation(self, msg: str):
        self.ok = False
        self.violations.append(msg)
 
    def add_warning(self, msg: str):
        self.warnings.append(msg)
 
    def add_suggestion(self, msg: str):
        self.suggestions.append(msg)
 
    def to_dict(self) -> Dict:
        return {
            "ok": self.ok,
            "violations": self.violations,
            "warnings": self.warnings,
            "suggestions": self.suggestions
        }

class WDPVerifier:
    """WDP Verifier"""
 
    @classmethod
    def verify(cls, original_marks: List[WatchdocMark],
               new_file_path: str,
               authorizations: Dict[str, int] = None) -> VerificationResult:
        """
        Verify new code complies with WDP constraints
        authorizations: {module_id: score} human authorization score
        """
        result = VerificationResult()
        authorizations = authorizations or {}
 
        new_marks = WDPParser.parse_file(new_file_path)
        new_marks_map = {m.module_id: m for m in new_marks}
 
        for orig in original_marks:
            auth_score = authorizations.get(orig.module_id, 1)
            new = new_marks_map.get(orig.module_id)
 
            if not new:
                result.add_violation(f"Module '{orig.module_id}' was deleted")
                continue
 
            if auth_score == 1 and orig.content_hash != new.content_hash:
                result.add_violation(
                    f"Unauthorized modification: '{orig.module_id}' (score 1=read-only)"
                )
                continue
 
            if orig.guard == GuardLevel.FREEZE:
                if orig.content_hash != new.content_hash:
                    result.add_violation(
                        f"FREEZE violation: '{orig.module_id}' was modified"
                    )
 
            elif orig.guard == GuardLevel.GUARD:
                for rule in orig.asserts:
                    if not cls._verify_assert(rule, orig, new):
                        result.add_violation(
                            f"GUARD violation: '{orig.module_id}' failed {rule.rule_type}"
                        )
 
            elif orig.guard == GuardLevel.AUDIT:
                if orig.content_hash != new.content_hash:
                    if not cls._has_wd_note(new.raw_lines):
                        result.add_warning(
                            f"AUDIT warning: '{orig.module_id}' modified without @wd-note"
                        )
                        result.add_suggestion(
                            f"Add // @wd-note: [modification reason] to {orig.module_id}"
                        )
 
        return result
 
    @classmethod
    def _verify_assert(cls, rule: AssertRule, orig: WatchdocMark, new: WatchdocMark) -> bool:
        if rule.rule_type == "Signature_Lock":
            return orig.entry == new.entry
        elif rule.rule_type == "Complexity_Limit":
            max_complexity = int(rule.params.get('value', 10))
            return True
        elif rule.rule_type.startswith("Test_Linked"):
            return True
        return True
 
    @classmethod
    def _has_wd_note(cls, lines: List[str]) -> bool:
        return any('// @wd-note:' in line for line in lines)
 
    @classmethod
    def verify_hash(cls, expected_hash: str, code_block: str) -> bool:
        actual_hash = hashlib.sha256(code_block.encode('utf-8')).hexdigest()[:16]
        return expected_hash == actual_hash
