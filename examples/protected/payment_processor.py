#!/usr/bin/env python3
"""
受 WDP 保护的支付处理核心逻辑 - 生产环境代码
此文件包含 FREEZE 保护标记，任何修改都将被拦截
"""

# @WDP: FREEZE | module-id=PAY-001 | role=Core | level=L0 | signature_lock=a1b2c3d4
def calculate_transaction_fee(amount: float, user_tier: str) -> float:
    """
    计算交易手续费 - 核心金融逻辑
    此函数已被 FREEZE 保护，禁止 AI 重构
    """
    if user_tier == "VIP":
        return amount * 0.005  # 0.5%
    elif user_tier == "PREMIUM":
        return amount * 0.01   # 1%
    else:
        return amount * 0.015  # 1.5%
# @WDP: END


# @WDP: GUARD | module-id=PAY-002 | role=Validation | level=L1
def validate_card_number(card_number: str) -> bool:
    """验证银行卡号格式（Luhn 算法）"""
    if not card_number.isdigit():
        return False
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    total = 0
    reverse_digits = card_number[::-1]
    
    for i, digit in enumerate(reverse_digits):
        d = int(digit)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    
    return total % 10 == 0
# @WDP: END


# @WDP: AUDIT | module-id=PAY-003 | role=Logging | level=L2
def log_transaction(transaction_id: str, amount: float, status: str):
    """记录交易日志 - 允许修改但需要审计"""
    timestamp = "2024-01-15 10:30:00"
    print(f"[{timestamp}] TXN:{transaction_id} | Amount:${amount:.2f} | Status:{status}")
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
