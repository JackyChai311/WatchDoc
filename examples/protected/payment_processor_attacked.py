#!/usr/bin/env python3
"""
被 AI 恶意重构后的支付处理代码 - 模拟攻击结果
AI 试图"优化"核心逻辑，但违反了 FREEZE 保护
"""

# @WDP: FREEZE | module-id=PAY-001 | role=Core | level=L0 | signature_lock=a1b2c3d4
def calculate_transaction_fee(amount: float, user_tier: str) -> float:
    """
    [AI 重构] 简化手续费计算逻辑
    AI 认为原逻辑过于复杂，进行了"优化"
    """
    # AI 错误地统一了费率，破坏了业务规则
    return amount * 0.01  # 全部改为 1%，破坏了 VIP/PREMIUM 差异化
# @WDP: END


# @WDP: GUARD | module-id=PAY-002 | role=Validation | level=L1
def validate_card_number(card_number: str) -> bool:
    """[AI 重构] 使用正则表达式简化验证"""
    import re
    # AI 移除了 Luhn 算法，只用正则检查格式，安全性大幅降低
    pattern = r'^\d{13,19}$'
    return bool(re.match(pattern, card_number))
# @WDP: END


# @WDP: AUDIT | module-id=PAY-003 | role=Logging | level=L2
def log_transaction(transaction_id: str, amount: float, status: str):
    """[AI 修改] 添加 JSON 格式输出"""
    import json
    from datetime import datetime
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "txn_id": transaction_id,
        "amount": amount,
        "status": status
    }
    print(json.dumps(log_entry))
# @WDP: END


def process_payment(user_id: str, amount: float, card_number: str, user_tier: str) -> dict:
    """处理支付请求的主流程"""
    
    # 验证卡号
    if not validate_card_number(card_number):
        return {"success": False, "error": "Invalid card number"}
    
    # 计算手续费
    fee = calculate_transaction_fee(amount, user_tier)
    total_amount = amount + fee
    
    # 生成交易 ID
    import hashlib
    transaction_id = hashlib.sha256(f"{user_id}{amount}{card_number}".encode()).hexdigest()[:12]
    
    # 记录日志
    log_transaction(transaction_id, total_amount, "PENDING")
    
    # 模拟支付处理
    log_transaction(transaction_id, total_amount, "COMPLETED")
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "amount": amount,
        "fee": fee,
        "total": total_amount
    }


if __name__ == "__main__":
    result = process_payment("USER123", 100.0, "4532015112830366", "VIP")
    print(f"支付结果：{result}")
