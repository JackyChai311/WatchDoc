#!/usr/bin/env python3
"""
Payment processor - ATTACKED VERSION (FREEZE block modified)
AI attempted to "optimize" core logic but violated FREEZE protection
"""

# @wd: FREEZE | module-id=PAY-001 | role=Core | level=L0 | signature_lock=a1b2c3d4
def calculate_transaction_fee(amount: float, user_tier: str) -> float:
    """[AI REFACTOR] Simplified fee calculation logic - BROKEN BUSINESS RULES"""
    # AI incorrectly unified all tiers to flat rate, breaking VIP/PREMIUM differentiation
    return amount * 0.01  # Flat 1% for ALL tiers - DESTROYS business logic
# @wd: END


# @wd: GUARD | module-id=PAY-002 | role=Validation | level=L1
def validate_card_number(card_number: str) -> bool:
    """[AI REFACTOR] Simplified validation with regex - SECURITY RISK"""
    import re
    # AI removed Luhn algorithm, only using regex - significantly reduced security
    pattern = r'^\d{13,19}$'
    return bool(re.match(pattern, card_number))
# @wd: END


# @wd: AUDIT | module-id=PAY-003 | role=Logging | level=L2
def log_transaction(transaction_id: str, amount: float, status: str):
    """[AI MODIFIED] Added JSON format output"""
    import json
    from datetime import datetime
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "txn_id": transaction_id,
        "amount": amount,
        "status": status
    }
    print(json.dumps(log_entry))
# @wd: END


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
