"""
Pytest configuration and fixtures for WatchDoc tests.
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_wdp_code():
    """Return a sample code snippet with WDP markers."""
    return '''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic - DO NOT MODIFY"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    // Core payment logic here
    return { success: true, transactionId: "txn_123" };
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}
// @wd: utils | END
'''


@pytest.fixture
def sample_python_code():
    """Return a sample Python code snippet with WDP markers."""
    return '''# @wd: payment-core | Role: Core | Guard: FREEZE | Entry: process_payment | Summary: "Core payment logic - DO NOT MODIFY"
# @wd-assert: Signature_Lock
def process_payment(amount, card_info):
    """Core payment logic here"""
    return {"success": True, "transactionId": "txn_123"}
# @wd: payment-core | END

# @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
def format_currency(amount):
    """Format currency"""
    return f"${amount:.2f}"
# @wd: utils | END
'''
