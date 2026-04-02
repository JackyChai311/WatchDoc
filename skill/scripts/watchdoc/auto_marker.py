#!/usr/bin/env python3
"""
WATCHDOC Auto Marker - Universal language code scanner and marker

Supports all major programming languages with configurable patterns.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .parser import WDPParser, WatchdocMark, GuardLevel, RoleType


# Universal language configuration
LANGUAGE_CONFIGS = {
    'python': {
        'extensions': ['.py'],
        'patterns': [
            (r'def\s+(\w+)\s*\([^)]*\)\s*:', 'function'),
            (r'async\s+def\s+(\w+)\s*\([^)]*\)\s*:', 'async_function'),
            (r'class\s+(\w+)\s*[:\(]', 'class'),
        ],
        'block_type': 'indent',
        'comment_style': '#'
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.mjs'],
        'patterns': [
            (r'function\s+(\w+)\s*\([^)]*\)\s*\{', 'function'),
            (r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', 'arrow'),
            (r'(?:const|let|var)\s+(\w+)\s*=\s*function\s*\([^)]*\)', 'function'),
            (r'export\s+(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{', 'export_function'),
            (r'export\s+(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', 'export_arrow'),
            (r'class\s+(\w+)\s*(?:extends\s+[\w\s]+)?\s*\{', 'class'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'typescript': {
        'extensions': ['.ts', '.tsx'],
        'patterns': [
            (r'function\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{', 'function'),
            (r'(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', 'arrow'),
            (r'export\s+(?:async\s+)?function\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{', 'export_function'),
            (r'export\s+(?:default\s+)?class\s+(\w+)\s*(?:<[^>]+>)?\s*(?:extends\s+[\w\s]+)?\s*\{', 'class'),
            (r'interface\s+(\w+)\s*(?:<[^>]+>)?\s*\{', 'interface'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'java': {
        'extensions': ['.java'],
        'patterns': [
            (r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{', 'method'),
            (r'(?:public|private|protected)?\s*(?:static\s+)?class\s+(\w+)\s*(?:<[^>]+>)?\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w,\s]+)?\s*\{', 'class'),
            (r'interface\s+(\w+)\s*(?:<[^>]+>)?\s*\{', 'interface'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'go': {
        'extensions': ['.go'],
        'patterns': [
            (r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\([^)]*\)\s*(?:\([^)]*\)|[\w\s,]+)?\s*\{', 'function'),
            (r'type\s+(\w+)\s+struct\s*\{', 'struct'),
            (r'type\s+(\w+)\s+interface\s*\{', 'interface'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'rust': {
        'extensions': ['.rs'],
        'patterns': [
            (r'(?:pub\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?:->\s*[\w<>]+)?\s*\{', 'function'),
            (r'(?:pub\s+)?struct\s+(\w+)\s*(?:<[^>]+>)?\s*\{', 'struct'),
            (r'(?:pub\s+)?enum\s+(\w+)\s*(?:<[^>]+>)?\s*\{', 'enum'),
            (r'(?:pub\s+)?trait\s+(\w+)\s*(?:<[^>]+>)?\s*\{', 'trait'),
            (r'impl\s+(?:<[^>]+>\s+)?(\w+)', 'impl'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'ruby': {
        'extensions': ['.rb', '.rake'],
        'patterns': [
            (r'def\s+(?:self\.)?(\w+)(?:[?!])?(?:\([^)]*\))?\s*$', 'method'),
            (r'class\s+(\w+)\s*(?:<\s*[\w:]+)?$', 'class'),
            (r'module\s+(\w+)\s*$', 'module'),
        ],
        'block_type': 'keyword_end',
        'comment_style': '#'
    },
    'php': {
        'extensions': ['.php'],
        'patterns': [
            (r'(?:public|private|protected)?\s*(?:static\s+)?function\s+(\w+)\s*\([^)]*\)\s*(?::\s*\??[\w\\]+)?\s*\{', 'function'),
            (r'class\s+(\w+)\s*(?:extends\s+[\w\\]+)?\s*(?:implements\s+[\w\\,\s]+)?\s*\{', 'class'),
            (r'trait\s+(\w+)\s*\{', 'trait'),
            (r'interface\s+(\w+)\s*\{', 'interface'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'c_cpp': {
        'extensions': ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx'],
        'patterns': [
            (r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{', 'function'),
            (r'class\s+(\w+)\s*(?::\s*[\w,\s]+)?\s*\{', 'class'),
            (r'struct\s+(\w+)\s*\{', 'struct'),
            (r'namespace\s+(\w+)\s*\{', 'namespace'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'swift': {
        'extensions': ['.swift'],
        'patterns': [
            (r'func\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?:->\s*[\w\[\]?]+)?\s*\{', 'function'),
            (r'class\s+(\w+)\s*(?::\s*[\w,\s]+)?\s*\{', 'class'),
            (r'struct\s+(\w+)\s*(?::\s*[\w,\s]+)?\s*\{', 'struct'),
            (r'enum\s+(\w+)\s*(?::\s*\w+)?\s*\{', 'enum'),
            (r'protocol\s+(\w+)\s*\{', 'protocol'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'kotlin': {
        'extensions': ['.kt', '.kts'],
        'patterns': [
            (r'fun\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?::\s*[\w<>?]+)?\s*\{', 'function'),
            (r'class\s+(\w+)\s*(?:<[^>]+>)?\s*(?::\s*[\w,\s]+)?\s*\{', 'class'),
            (r'object\s+(\w+)\s*\{', 'object'),
            (r'interface\s+(\w+)\s*\{', 'interface'),
            (r'data\s+class\s+(\w+)\s*\([^)]*\)\s*\{', 'data_class'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'scala': {
        'extensions': ['.scala'],
        'patterns': [
            (r'def\s+(\w+)\s*(?:\[[^\]]+\])?\s*\([^)]*\)\s*(?::\s*[\w\[\],\s]+)?\s*=?\s*\{', 'function'),
            (r'class\s+(\w+)\s*(?:\[[^\]]+\])?\s*(?:extends\s+[\w,\s]+)?\s*\{', 'class'),
            (r'object\s+(\w+)\s*(?:extends\s+[\w,\s]+)?\s*\{', 'object'),
            (r'trait\s+(\w+)\s*(?:\[[^\]]+\])?\s*\{', 'trait'),
            (r'case\s+class\s+(\w+)\s*\([^)]*\)', 'case_class'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'csharp': {
        'extensions': ['.cs'],
        'patterns': [
            (r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:[\w<>]+)\s+(\w+)\s*\([^)]*\)\s*\{', 'method'),
            (r'(?:public|private|protected|internal)?\s*(?:static\s+)?class\s+(\w+)\s*(?::\s*[\w,\s]+)?\s*\{', 'class'),
            (r'interface\s+(\w+)\s*\{', 'interface'),
            (r'struct\s+(\w+)\s*\{', 'struct'),
        ],
        'block_type': 'brace',
        'comment_style': '//'
    },
    'bash': {
        'extensions': ['.sh', '.bash'],
        'patterns': [
            (r'function\s+(\w+)\s*\(\)\s*\{', 'function'),
            (r'^(\w+)\s*\(\)\s*\{', 'function'),
        ],
        'block_type': 'brace',
        'comment_style': '#'
    },
    'lua': {
        'extensions': ['.lua'],
        'patterns': [
            (r'function\s+(\w+(?:\.\w+)?)\s*\([^)]*\)', 'function'),
            (r'local\s+function\s+(\w+)\s*\([^)]*\)', 'local_function'),
        ],
        'block_type': 'keyword_end',
        'comment_style': '--'
    },
    'perl': {
        'extensions': ['.pl', '.pm'],
        'patterns': [
            (r'sub\s+(\w+)\s*\{', 'subroutine'),
            (r'package\s+(\w+);', 'package'),
        ],
        'block_type': 'brace',
        'comment_style': '#'
    },
    'r': {
        'extensions': ['.r', '.R'],
        'patterns': [
            (r'(\w+)\s*<-\s*function\s*\([^)]*\)\s*\{', 'function'),
            (r'(\w+)\s*=\s*function\s*\([^)]*\)\s*\{', 'function'),
        ],
        'block_type': 'brace',
        'comment_style': '#'
    },
}


class AutoMarker:
    """Auto-scan code and add @wd markers for all languages"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.supported_extensions = self._get_all_extensions()
    
    def _get_all_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        extensions = []
        for config in LANGUAGE_CONFIGS.values():
            extensions.extend(config['extensions'])
        return list(set(extensions))
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language based on file extension"""
        ext = file_path.suffix.lower()
        for lang, config in LANGUAGE_CONFIGS.items():
            if ext in config['extensions']:
                return lang
        return None
    
    def scan_and_mark_all(self, default_guard: GuardLevel = GuardLevel.FREEZE) -> Dict:
        """Scan project and auto-mark all functions across all languages"""
        results = {
            "total_files": 0,
            "total_functions": 0,
            "marked_files": [],
            "errors": [],
            "language_stats": {}
        }
        
        for ext in self.supported_extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                if self._should_skip(file_path):
                    continue
                
                try:
                    marked_count = self._mark_file(file_path, default_guard)
                    if marked_count > 0:
                        rel_path = str(file_path.relative_to(self.project_root))
                        lang = self._detect_language(file_path)
                        
                        results["marked_files"].append({
                            "file": rel_path,
                            "language": lang,
                            "functions_marked": marked_count
                        })
                        results["total_functions"] += marked_count
                        
                        # Track language statistics
                        if lang:
                            results["language_stats"][lang] = \
                                results["language_stats"].get(lang, 0) + marked_count
                    
                    results["total_files"] += 1
                except Exception as e:
                    results["errors"].append(f"{file_path}: {str(e)}")
        
        return results
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'node_modules', '.git', '__pycache__', 'venv', 'env', 
            'build', 'dist', 'target', 'vendor', '.idea', '.vscode',
            'Pods', 'Carthage', 'DerivedData'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _mark_file(self, file_path: Path, default_guard: GuardLevel) -> int:
        """Mark all functions in a single file"""
        # Check if already has @wd markers
        existing_marks = WDPParser.parse_file(str(file_path))
        if existing_marks:
            return 0  # Already marked, skip
        
        # Detect language
        language = self._detect_language(file_path)
        if not language:
            return 0
        
        # Extract functions based on language
        if language == 'python':
            functions = self._extract_python_functions(file_path)
        else:
            functions = self._extract_functions_universal(file_path, language)
        
        if not functions:
            return 0
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Add @wd markers for each function
        marked_count = 0
        offset = 0
        comment_style = LANGUAGE_CONFIGS[language]['comment_style']
        
        # Process functions in reverse order to avoid offset issues
        for func in sorted(functions, key=lambda x: x['line'], reverse=True):
            module_id = self._generate_module_id(file_path, func['name'])
            
            # Generate @wd marker
            wd_marker = self._generate_wd_marker(module_id, func, default_guard, comment_style, file_path)
            end_marker = f"{comment_style} @wd: {module_id} | END\n"
            
            # Calculate insertion positions BEFORE any insertions
            marker_insert_idx = func['line'] - 1
            end_insert_idx = func['end_line']  # Insert after the last line
            
            # Insert END marker first (working backwards)
            lines.insert(end_insert_idx, end_marker)
            
            # Then insert marker before function
            lines.insert(marker_insert_idx, wd_marker + '\n')
            
            marked_count += 1
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return marked_count
    
    def _extract_python_functions(self, file_path: Path) -> List[Dict]:
        """Extract all functions from Python file using AST"""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'end_line': node.end_lineno or node.lineno + 1,
                        'type': 'function'
                    })
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'end_line': node.end_lineno or node.lineno + 1,
                        'type': 'async_function'
                    })
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
        return functions
    
    def _extract_functions_universal(self, file_path: Path, language: str) -> List[Dict]:
        """Universal function extractor for all languages"""
        functions = []
        
        config = LANGUAGE_CONFIGS.get(language)
        if not config:
            return functions
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Apply all patterns for this language
            for pattern, func_type in config['patterns']:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    start_pos = match.start()
                    func_name = match.group(1)
                    
                    # Calculate line number
                    line_num = content[:start_pos].count('\n') + 1
                    
                    # Find function end based on block type
                    end_line = self._find_function_end(
                        lines, 
                        line_num - 1, 
                        config['block_type']
                    )
                    
                    # Avoid duplicates
                    if not any(f['name'] == func_name and f['line'] == line_num for f in functions):
                        functions.append({
                            'name': func_name,
                            'line': line_num,
                            'end_line': end_line,
                            'type': func_type
                        })
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return functions
    
    def _find_function_end(self, lines: List[str], start_line: int, block_type: str) -> int:
        """Find the end line of a function based on block type"""
        
        if block_type == 'brace':
            # C-style: match { and }
            brace_count = 0
            in_function = False
            
            for i in range(start_line, min(start_line + 200, len(lines))):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                
                if '{' in line and not in_function:
                    in_function = True
                
                if in_function and brace_count == 0:
                    return i + 1  # Return 1-indexed line number
            
            return start_line + 10  # Default estimate
        
        elif block_type == 'indent':
            # Python-style: find dedent
            if start_line >= len(lines):
                return start_line + 1
            
            # Get function's indentation level (from the line after def)
            # Skip to first non-empty line after function definition
            func_indent = None
            for i in range(start_line, min(start_line + 3, len(lines))):
                line = lines[i]
                if line.strip() and not line.strip().startswith('#'):
                    if 'def ' in line or 'class ' in line:
                        # This is the def line, next line is the body
                        continue
                    elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                        # Docstring, skip
                        continue
                    else:
                        # First line of function body
                        func_indent = len(line) - len(line.lstrip())
                        break
            
            if func_indent is None:
                return start_line + 10
            
            # Find the end of the function
            for i in range(start_line + 1, min(start_line + 100, len(lines))):
                line = lines[i]
                
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                # Check if this line is at same or lower indentation
                current_indent = len(line) - len(line.lstrip())
                if current_indent < func_indent:
                    return i  # Return before this line (this line is outside function)
                elif current_indent == func_indent and not line.strip().startswith(('def ', 'class ', '@')):
                    # Continue in same function
                    continue
            
            return min(start_line + 20, len(lines))
        
        elif block_type == 'keyword_end':
            # Ruby/Lua style: find matching 'end'
            depth = 1
            
            for i in range(start_line + 1, min(start_line + 200, len(lines))):
                line = lines[i].strip()
                
                # Count block openers
                if any(line.startswith(kw) for kw in ['def ', 'class ', 'module ', 'do', 'begin', 'if ', 'unless ']):
                    depth += 1
                
                # Count 'end'
                if line == 'end' or line.startswith('end ') or line.startswith('end#'):
                    depth -= 1
                    if depth == 0:
                        return i + 1
            
            return start_line + 10
        
        else:
            return start_line + 10  # Default
    
    def _generate_module_id(self, file_path: Path, func_name: str) -> str:
        """Generate unique module ID"""
        file_stem = file_path.stem
        return f"{file_stem}_{func_name}"
    
    def _generate_wd_marker(self, module_id: str, func_info: Dict, guard: GuardLevel, comment_style: str, file_path: Path = None) -> str:
        """Generate @wd marker with proper comment style"""
        role = self._infer_role(func_info['name'])
        
        # 
        summary = self._generate_summary(func_info, file_path)
        
        return f"{comment_style} @wd: {module_id} | Role: {role.value} | Guard: {guard.value} | Summary: \"{summary}\""
    
    def _generate_summary(self, func_info: Dict, file_path: Path = None) -> str:
        """Generate function summary based on function name, docstring, or context"""
        
        # 1.  docstring
        if file_path and file_path.suffix == '.py':
            docstring = self._extract_python_docstring(file_path, func_info['line'])
            if docstring:
                return docstring
        
        # 2. 
        func_name = func_info['name']
        summary = self._infer_function_purpose(func_name)
        
        return summary
    
    def _extract_python_docstring(self, file_path: Path, func_line: int) -> Optional[str]:
        """Extract docstring from Python function"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 
            for i in range(func_line, min(func_line + 5, len(lines))):
                line = lines[i].strip()
                
                # 
                if not line:
                    continue
                
                #  docstring
                if line.startswith('"""') or line.startswith("'''"):
                    #  docstring
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        return line.strip('"\'').strip()
                    
                    #  docstring
                    quote = '"""' if line.startswith('"""') else "'''"
                    docstring_lines = [line.lstrip('"\'')]
                    
                    for j in range(i + 1, min(i + 20, len(lines))):
                        doc_line = lines[j].rstrip()
                        if quote in doc_line:
                            docstring_lines.append(doc_line.split(quote)[0])
                            break
                        docstring_lines.append(doc_line)
                    
                    # 
                    full_docstring = ' '.join(docstring_lines).strip()
                    # 
                    if '.' in full_docstring:
                        full_docstring = full_docstring.split('.')[0] + '.'
                    return full_docstring[:100]  # 
            
        except Exception:
            pass
        
        return None
    
    def _infer_function_purpose(self, func_name: str) -> str:
        """Infer function purpose from function name using pattern matching"""
        
        func_lower = func_name.lower()
        
        # 
        verb_patterns = {
            'get': 'Get',
            'set': 'Set',
            'calculate': 'Calculate',
            'compute': 'Compute',
            'process': 'Process',
            'handle': 'Handle',
            'validate': 'Validate',
            'check': 'Check',
            'verify': 'Verify',
            'parse': 'Parse',
            'format': 'Format',
            'convert': 'Convert',
            'load': 'Load',
            'save': 'Save',
            'init': 'Initialize',
            'create': 'Create',
            'delete': 'Delete',
            'update': 'Update',
            'send': 'Send',
            'receive': 'Receive',
            'fetch': 'Fetch',
            'render': 'Render',
            'display': 'Display',
            'start': 'Start',
            'stop': 'Stop',
            'run': 'Run',
            'execute': 'Execute',
            'build': 'Build',
            'generate': 'Generate',
            'extract': 'Extract',
            'transform': 'Transform',
            'analyze': 'Analyze',
            'evaluate': 'Evaluate',
            'test': 'Test',
            'mock': 'Mock',
            'clean': 'Clean',
            'reset': 'Reset',
            'reset': 'Reset',
            'clear': 'Clear',
            'reset': 'Reset',
            'add': 'Add',
            'remove': 'Remove',
            'insert': 'Insert',
            'append': 'Append',
            'push': 'Push',
            'pop': 'Pop',
            'read': 'Read',
            'write': 'Write',
            'open': 'Open',
            'close': 'Close',
            'connect': 'Connect',
            'disconnect': 'Disconnect',
            'login': 'Login',
            'logout': 'Logout',
            'register': 'Register',
            'unregister': 'Unregister',
            'subscribe': 'Subscribe',
            'unsubscribe': 'Unsubscribe',
            'publish': 'Publish',
            'emit': 'Emit',
        }
        
        # 
        noun_patterns = {
            'payment': 'payment',
            'order': 'order',
            'user': 'user',
            'customer': 'customer',
            'product': 'product',
            'item': 'item',
            'cart': 'cart',
            'checkout': 'checkout',
            'invoice': 'invoice',
            'receipt': 'receipt',
            'transaction': 'transaction',
            'account': 'account',
            'profile': 'profile',
            'setting': 'settings',
            'config': 'configuration',
            'data': 'data',
            'file': 'file',
            'image': 'image',
            'video': 'video',
            'audio': 'audio',
            'text': 'text',
            'message': 'message',
            'email': 'email',
            'notification': 'notification',
            'log': 'log',
            'error': 'error',
            'warning': 'warning',
            'exception': 'exception',
            'timeout': 'timeout',
            'cache': 'cache',
            'token': 'token',
            'session': 'session',
            'cookie': 'cookie',
            'header': 'header',
            'request': 'request',
            'response': 'response',
            'api': 'API',
            'database': 'database',
            'db': 'database',
            'query': 'query',
            'table': 'table',
            'record': 'record',
            'field': 'field',
            'column': 'column',
            'row': 'row',
            'index': 'index',
            'key': 'key',
            'value': 'value',
            'type': 'type',
            'status': 'status',
            'state': 'state',
            'result': 'result',
            'output': 'output',
            'input': 'input',
            'param': 'parameter',
            'arg': 'argument',
            'option': 'option',
            'flag': 'flag',
            'switch': 'switch',
            'button': 'button',
            'link': 'link',
            'page': 'page',
            'view': 'view',
            'modal': 'modal',
            'dialog': 'dialog',
            'form': 'form',
            'field': 'field',
            'list': 'list',
            'array': 'array',
            'object': 'object',
            'string': 'string',
            'number': 'number',
            'integer': 'integer',
            'float': 'float',
            'boolean': 'boolean',
            'date': 'date',
            'time': 'time',
            'timestamp': 'timestamp',
            'url': 'URL',
            'uri': 'URI',
            'path': 'path',
            'route': 'route',
            'endpoint': 'endpoint',
            'callback': 'callback',
            'handler': 'handler',
            'listener': 'listener',
            'event': 'event',
            'action': 'action',
            'task': 'task',
            'job': 'job',
            'worker': 'worker',
            'thread': 'thread',
            'process': 'process',
            'service': 'service',
            'client': 'client',
            'server': 'server',
            'socket': 'socket',
            'connection': 'connection',
            'stream': 'stream',
            'buffer': 'buffer',
            'queue': 'queue',
            'stack': 'stack',
            'heap': 'heap',
            'tree': 'tree',
            'graph': 'graph',
            'node': 'node',
            'edge': 'edge',
            'vertex': 'vertex',
        }
        
        # 
        # 
        import re
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', func_name)
        if not words:
            words = [func_name]
        
        # 
        parts = []
        
        for word in words:
            word_lower = word.lower()
            
            # 
            if word_lower in verb_patterns:
                parts.append(verb_patterns[word_lower])
            # 
            elif word_lower in noun_patterns:
                parts.append(noun_patterns[word_lower])
            # （）
            else:
                # （），
                if word.isupper():
                    parts.append(word)
                else:
                    parts.append(word.lower())
        
        # ，
        if parts and parts[0] not in verb_patterns.values():
            parts.insert(0, 'Handle')
        
        # 
        if len(parts) == 0:
            return f"Function for {func_name}"
        elif len(parts) == 1:
            return f"{parts[0]} operation"
        else:
            # ，
            return ' '.join(parts)
    
    def _infer_role(self, func_name: str) -> RoleType:
        """Infer role type based on function name"""
        func_lower = func_name.lower()
        
        if any(k in func_lower for k in ['config', 'setting', 'init']):
            return RoleType.CONFIG
        elif any(k in func_lower for k in ['calculate', 'compute', 'process']):
            return RoleType.CORE
        elif any(k in func_lower for k in ['format', 'parse', 'convert', 'validate', 'check', 'verify']):
            return RoleType.UTIL
        elif any(k in func_lower for k in ['send', 'receive', 'request', 'api', 'fetch']):
            return RoleType.INTERFACE
        else:
            return RoleType.CORE


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_marker.py <project_root> [--guard=FREEZE|WARN|AUDIT]")
        print("\nSupported languages:")
        for lang in sorted(LANGUAGE_CONFIGS.keys()):
            exts = ', '.join(LANGUAGE_CONFIGS[lang]['extensions'])
            print(f"  - {lang}: {exts}")
        sys.exit(1)
    
    project_root = sys.argv[1]
    guard_level = GuardLevel.FREEZE
    
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg.startswith('--guard='):
                guard_name = arg.split('=')[1].upper()
                guard_level = GuardLevel(guard_name)
    
    marker = AutoMarker(project_root)
    results = marker.scan_and_mark_all(guard_level)
    
    print(f"\n✅ Scan complete!")
    print(f"Total files scanned: {results['total_files']}")
    print(f"Total functions marked: {results['total_functions']}")
    print(f"\nLanguages detected:")
    for lang, count in sorted(results['language_stats'].items()):
        print(f"  - {lang}: {count} functions")
    
    if results['errors']:
        print(f"\n⚠️ Errors:")
        for error in results['errors']:
            print(f"  - {error}")


if __name__ == '__main__':
    main()
