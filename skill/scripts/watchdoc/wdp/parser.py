#!/usr/bin/env python3
"""
WATCHDOC Protocol Parser - WDP-1.1
Parse @wd markers in code，extract protection rules
"""

import re
import hashlib
import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class GuardLevel(Enum):
    FREEZE = "FREEZE"
    GUARD = "GUARD"
    AUDIT = "AUDIT"
    NONE = "NONE"

class RoleType(Enum):
    CORE = "Core"
    UTIL = "Util"
    INTERFACE = "Interface"
    CONFIG = "Config"
    LEGACY = "Legacy"

@dataclass
class AssertRule:
    rule_type: str
    params: Dict[str, str]
 
    @classmethod
    def parse(cls, raw: str) -> Optional['AssertRule']:
        if ':' not in raw:
            return None
        rule_type, _, params_str = raw.partition(':')
        params = {}
        if ',' in params_str:
            for kv in params_str.split(','):
                if ':' in kv:
                    k, v = kv.split(':', 1)
                    params[k.strip()] = v.strip()
        elif params_str:
            params['value'] = params_str
        return cls(rule_type=rule_type.strip(), params=params)

@dataclass
class WatchdocMark:
    """WDP marker complete definition"""
    module_id: str
    role: RoleType
    guard: GuardLevel
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    entry: Optional[str] = None
    depends: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    asserts: List[AssertRule] = field(default_factory=list)
    content_hash: str = ""
    raw_lines: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
 
    def to_dict(self) -> Dict:
        return {
            "module_id": self.module_id,
            "role": self.role.value,
            "guard": self.guard.value,
            "file": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "entry": self.entry,
            "depends": self.depends,
            "summary": self.summary,
            "asserts": [{"type": a.rule_type, "params": a.params} for a in self.asserts],
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
 
    @classmethod
    def from_dict(cls, data: Dict) -> 'WatchdocMark':
        return cls(
            module_id=data["module_id"],
            role=RoleType(data["role"]),
            guard=GuardLevel(data["guard"]),
            file_path=data.get("file", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            entry=data.get("entry"),
            depends=data.get("depends", []),
            summary=data.get("summary"),
            asserts=[AssertRule(a["type"], a["params"]) for a in data.get("asserts", [])],
            content_hash=data.get("content_hash", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )

class WDPParser:
    """WDP """
 
    MARK_PATTERN = re.compile(
        r'//\s*@wd:\s*(?P<id>\w[\w\-]*)\s*\|(?P<fields>.+)',
        re.IGNORECASE
    )
 
    FIELD_PATTERN = re.compile(r'(\w+):\s*([^|]+?)(?=\s*\||\s*$)')
    ASSERT_PATTERN = re.compile(r'//\s*@wd-assert:\s*(.+)', re.IGNORECASE)
 
    @classmethod
    def parse_line(cls, line: str, line_num: int, file_path: str) -> Optional[WatchdocMark]:
        match = cls.MARK_PATTERN.match(line.strip())
        if not match or '| END' in line:
            return None
 
        module_id = match.group('id')
        fields_str = match.group('fields')
 
        fields = {}
        for field_match in cls.FIELD_PATTERN.finditer(fields_str):
            key, val = field_match.groups()
            fields[key.strip()] = val.strip().strip('"')
 
        if 'Role' not in fields or 'Guard' not in fields:
            return None
 
        asserts = []
        return WatchdocMark(
            module_id=module_id,
            role=RoleType(fields['Role']),
            guard=GuardLevel(fields['Guard']),
            entry=fields.get('Entry'),
            depends=[d.strip() for d in fields.get('Depends', '').split(',') if d.strip()],
            summary=fields.get('Summary'),
            file_path=file_path,
            line_start=line_num,
            asserts=asserts
        )
 
    @classmethod
    def parse_file(cls, file_path: str) -> List[WatchdocMark]:
        marks = []
        stack = []
 
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
 
        for i, line in enumerate(lines, 1):
            mark = cls.parse_line(line, i, file_path)
            if mark and mark.module_id not in [m.module_id for m in stack]:
                mark.raw_lines.append(line.rstrip())
                stack.append(mark)
                continue
 
            assert_match = cls.ASSERT_PATTERN.match(line.strip())
            if assert_match and stack:
                rule = AssertRule.parse(assert_match.group(1))
                if rule:
                    stack[-1].asserts.append(rule)
                stack[-1].raw_lines.append(line.rstrip())
                continue
 
            if '// @wd:' in line and '| END' in line:
                match = re.match(r'//\s*@wd:\s*(\w[\w\-]*)\s*\|\s*END', line.strip(), re.I)
                if match:
                    module_id = match.group(1)
                    for m in reversed(stack):
                        if m.module_id == module_id:
                            m.line_end = i
                            m.raw_lines.append(line.rstrip())
                            m.content_hash = cls._hash_block(lines[m.line_start-1:m.line_end])
                            marks.append(m)
                            stack.remove(m)
                            break
            elif stack:
                for m in stack:
                    m.raw_lines.append(line.rstrip())
 
        return marks
 
    @staticmethod
    def _hash_block(lines: List[str]) -> str:
        code = '\n'.join(line for line in lines
                        if not line.strip().startswith('// @wd:'))
        return hashlib.sha256(code.encode('utf-8')).hexdigest()[:16]
 
    @classmethod
    def parse_project(cls, project_root: str, extensions: List[str] = None) -> List[WatchdocMark]:
        extensions = extensions or ['.py', '.js', '.ts', '.java', '.go']
        all_marks = []
 
        for ext in extensions:
            for file_path in Path(project_root).rglob(f'*{ext}'):
                if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__']):
                    continue
                marks = cls.parse_file(str(file_path))
                all_marks.extend(marks)
 
        return all_marks
