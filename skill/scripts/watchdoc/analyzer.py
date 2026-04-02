#!/usr/bin/env python3
"""
WATCHDOC Impact Analyzer - A/B/C classify
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from datetime import datetime
from ..wdp.parser import WDPParser, WatchdocMark, GuardLevel
from ..wgw.authorization import FunctionCategory, AuthorizationScore

class ImpactAnalyzer:
    """ - A/B/C """
 
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.functions: Dict[str, WatchdocMark] = {}
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
 
    def index_project(self, extensions: List[str] = None):
        """"""
        extensions = extensions or ['.py', '.js', '.ts']
        all_marks = []
 
        for ext in extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__']):
                    continue
                marks = WDPParser.parse_file(str(file_path))
                all_marks.extend(marks)
 
        for mark in all_marks:
            self.functions[mark.module_id] = mark
 
        self._build_call_graph()
 
    def _build_call_graph(self):
        """"""
        for func_id, func in self.functions.items():
            for dep in func.depends:
                if dep in self.functions:
                    self.call_graph[func_id].add(dep)
                    self.reverse_graph[dep].add(func_id)
 
    def analyze(self, user_intent: str) -> Dict:
        """"""
        category_a = self._semantic_match(user_intent)
        a_ids = {f.module_id for f in category_a}
 
        category_b = self._trace_graph(a_ids, depth=2)
        b_ids = {f.module_id for f in category_b}
 
        c_count = len(self.functions) - len(a_ids) - len(b_ids)
 
        self._auto_score(category_a, category_b, user_intent)
 
        return {
            "session_id": f"ANALYSIS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_intent": user_intent,
            "category_a": [f.to_dict() for f in category_a],
            "category_b": [f.to_dict() for f in category_b],
            "category_c_count": c_count,
            "total_functions": len(self.functions),
            "timestamp": datetime.now().isoformat()
        }
 
    def _semantic_match(self, user_intent: str) -> List[WatchdocMark]:
        """A ："""
        matches = []
        keywords = self._extract_keywords(user_intent)
 
        for func in self.functions.values():
            score = 0
            reasons = []
 
            for keyword in keywords:
                if keyword.lower() in func.module_id.lower():
                    score += 3
                    reasons.append(f"ID '{keyword}'")
                if keyword.lower() in func.file_path.lower():
                    score += 2
                    reasons.append(f"path'{keyword}'")
 
            if '' in user_intent or 'config' in user_intent.lower():
                if func.role.value == 'Config':
                    score += 5
                    reasons.append("")
 
            if score >= 3:
                func.match_reason = "; ".join(reasons)
                func.category = FunctionCategory.A
                matches.append(func)
 
        return sorted(matches, key=lambda f: len(getattr(f, 'match_reason', '')), reverse=True)[:20]
 
    def _trace_graph(self, seed_ids: Set[str], depth: int = 2) -> List[WatchdocMark]:
        """B ："""
        visited = set(seed_ids)
        current_level = seed_ids
        b_functions = []
 
        for d in range(depth):
            next_level = set()
            for func_id in current_level:
                for called in self.call_graph.get(func_id, []):
                    if called not in visited and called in self.functions:
                        next_level.add(called)
                        visited.add(called)
                for caller in self.reverse_graph.get(func_id, []):
                    if caller not in visited and caller in self.functions:
                        next_level.add(caller)
                        visited.add(caller)
 
            for func_id in next_level:
                func = self.functions[func_id]
                func.category = FunctionCategory.B
                b_functions.append(func)
 
            current_level = next_level
            if not current_level:
                break
 
        return b_functions
 
    def _auto_score(self, category_a: List[WatchdocMark],
                    category_b: List[WatchdocMark],
                    user_intent: str):
        """"""
        change_type = self._detect_change_type(user_intent)
 
        for func in category_a:
            if func.guard == GuardLevel.FREEZE:
                func.authorization_score = 1
            elif change_type == 'CONFIG':
                func.authorization_score = 3
            elif func.guard == GuardLevel.NONE:
                func.authorization_score = 3
            else:
                func.authorization_score = 2
 
        for func in category_b:
            func.authorization_score = 1
 
    def _extract_keywords(self, text: str) -> List[str]:
        keywords = re.findall(r'[\w\u4e00-\u9fa5]+', text)
        stopwords = {'', '', '', '', '', '', '', 'a', 'an', 'the', 'to', 'for'}
        return [k for k in keywords if k.lower() not in stopwords and len(k) > 1]
 
    def _detect_change_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        if any(k in intent_lower for k in ['', 'config', 'setting']):
            return 'CONFIG'
        elif any(k in intent_lower for k in ['', 'fix', 'bug']):
            return 'BUGFIX'
        elif any(k in intent_lower for k in ['', 'refactor']):
            return 'REFACTOR'
        elif any(k in intent_lower for k in ['Add', 'add', 'new']):
            return 'FEATURE'
        return 'UNKNOWN'
