#!/usr/bin/env python3
"""
WDP 协议验证器 - 核心引擎
功能：解析 @WDP 标记，检测变更，判定违规
"""

import re
import sys
import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class WDPBlock:
    """WDP 保护块定义"""
    block_type: str  # FREEZE, GUARD, AUDIT
    module_id: str
    start_line: int
    end_line: int
    content_hash: str
    signature_lock: Optional[str] = None

@dataclass
class Violation:
    """违规记录"""
    severity: str  # CRITICAL, WARNING, INFO
    message: str
    line_number: int
    module_id: str

class WDPVerifier:
    def __init__(self):
        self.blocks: List[WDPBlock] = []
        self.violations: List[Violation] = []
        
    def parse_wdp_markers(self, code: str) -> List[WDPBlock]:
        """解析代码中的 WDP 标记"""
        blocks = []
        lines = code.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # 匹配开始标记: # @WDP: BLOCK_TYPE | module-id=XXX | ...
            match = re.match(r'#\s*@WDP:\s*(FREEZE|GUARD|AUDIT)\s*\|', line)
            if match:
                block_type = match.group(1)
                # 提取模块 ID
                module_match = re.search(r'module-id=([A-Z0-9\-]+)', line)
                module_id = module_match.group(1) if module_match else "UNKNOWN"
                
                start_line = i + 1
                content_lines = []
                end_line = start_line
                
                # 查找结束标记
                j = i + 1
                while j < len(lines):
                    if '# @WDP: END' in lines[j]:
                        end_line = j + 1
                        break
                    content_lines.append(lines[j])
                    j += 1
                else:
                    # 未找到结束标记，视为错误
                    end_line = len(lines)
                
                # 计算内容哈希
                content = '\n'.join(content_lines)
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                
                # 提取签名锁（如果有）
                sig_match = re.search(r'signature_lock=([a-f0-9]+)', line)
                signature_lock = sig_match.group(1) if sig_match else None
                
                blocks.append(WDPBlock(
                    block_type=block_type,
                    module_id=module_id,
                    start_line=start_line,
                    end_line=end_line,
                    content_hash=content_hash,
                    signature_lock=signature_lock
                ))
                
                i = end_line
            else:
                i += 1
        
        return blocks
    
    def verify(self, original_code: str, modified_code: str) -> List[Violation]:
        """对比原始代码和修改后代码，检测违规"""
        self.violations = []
        original_blocks = self.parse_wdp_markers(original_code)
        modified_blocks = self.parse_wdp_markers(modified_code)
        
        # 检查每个原始保护块
        for orig_block in original_blocks:
            # 在修改后的代码中查找对应的块
            found_block = None
            for mod_block in modified_blocks:
                if mod_block.module_id == orig_block.module_id and mod_block.block_type == orig_block.block_type:
                    found_block = mod_block
                    break
            
            if not found_block:
                # 保护块被删除
                self.violations.append(Violation(
                    severity="CRITICAL",
                    message=f"保护块被删除：{orig_block.block_type} 模块 {orig_block.module_id}",
                    line_number=orig_block.start_line,
                    module_id=orig_block.module_id
                ))
                continue
            
            # 检查内容是否变更
            if orig_block.content_hash != found_block.content_hash:
                if orig_block.block_type == "FREEZE":
                    self.violations.append(Violation(
                        severity="CRITICAL",
                        message=f"FREEZE 块内容被篡改：模块 {orig_block.module_id} (哈希变化：{orig_block.content_hash} -> {found_block.content_hash})",
                        line_number=found_block.start_line,
                        module_id=orig_block.module_id
                    ))
                elif orig_block.block_type == "GUARD":
                    self.violations.append(Violation(
                        severity="WARNING",
                        message=f"GUARD 块内容被修改：模块 {orig_block.module_id}",
                        line_number=found_block.start_line,
                        module_id=orig_block.module_id
                    ))
                elif orig_block.block_type == "AUDIT":
                    self.violations.append(Violation(
                        severity="INFO",
                        message=f"AUDIT 块内容被修改：模块 {orig_block.module_id} (需要审计)",
                        line_number=found_block.start_line,
                        module_id=orig_block.module_id
                    ))
            
            # 检查签名锁
            if orig_block.signature_lock and orig_block.signature_lock != found_block.signature_lock:
                self.violations.append(Violation(
                    severity="CRITICAL",
                    message=f"签名锁验证失败：模块 {orig_block.module_id}",
                    line_number=found_block.start_line,
                    module_id=orig_block.module_id
                ))
        
        # 检查是否有新的保护块被添加（可能是注入攻击）
        orig_module_ids = {b.module_id for b in original_blocks}
        for mod_block in modified_blocks:
            if mod_block.module_id not in orig_module_ids:
                self.violations.append(Violation(
                    severity="WARNING",
                    message=f"检测到新的保护块注入：{mod_block.block_type} 模块 {mod_block.module_id}",
                    line_number=mod_block.start_line,
                    module_id=mod_block.module_id
                ))
        
        return self.violations
    
    def generate_report(self) -> str:
        """生成违规报告"""
        if not self.violations:
            return "✅ 无违规检测到。代码符合 WDP 协议。"
        
        report = ["❌ 检测到 WDP 协议违规:\n"]
        critical_count = sum(1 for v in self.violations if v.severity == "CRITICAL")
        warning_count = sum(1 for v in self.violations if v.severity == "WARNING")
        info_count = sum(1 for v in self.violations if v.severity == "INFO")
        
        report.append(f"统计：{critical_count} 严重 | {warning_count} 警告 | {info_count} 提示\n")
        report.append("-" * 60 + "\n")
        
        for v in sorted(self.violations, key=lambda x: {"CRITICAL": 0, "WARNING": 1, "INFO": 2}[x.severity]):
            report.append(f"[{v.severity}] 行 {v.line_number} | 模块 {v.module_id}\n")
            report.append(f"  → {v.message}\n\n")
        
        return "".join(report)


def main():
    if len(sys.argv) < 3:
        print("用法：python wdp_verify.py <原始文件> <修改后文件>")
        print("退出码：0=无违规，1=有违规")
        sys.exit(2)
    
    original_file = sys.argv[1]
    modified_file = sys.argv[2]
    
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_code = f.read()
        with open(modified_file, 'r', encoding='utf-8') as f:
            modified_code = f.read()
    except FileNotFoundError as e:
        print(f"错误：文件不存在 - {e}")
        sys.exit(2)
    
    verifier = WDPVerifier()
    violations = verifier.verify(original_code, modified_code)
    report = verifier.generate_report()
    
    print(report)
    
    # 如果有严重违规，返回非零退出码（用于 CI/CD）
    has_critical = any(v.severity == "CRITICAL" for v in violations)
    sys.exit(1 if has_critical or violations else 0)


if __name__ == "__main__":
    main()
