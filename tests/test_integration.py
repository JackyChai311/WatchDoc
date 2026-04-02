"""
Integration tests for WatchDoc.
"""
import pytest
import tempfile
from pathlib import Path
from watchdoc.wdp.parser import WDPParser
from watchdoc.wdp.verifier import WDPVerifier


class TestIntegration:
    """Integration test cases."""

    def test_complete_workflow(self, temp_dir):
        """Test a complete WatchDoc workflow."""
        # 1. Create a sample project
        project_dir = temp_dir / "myproject"
        project_dir.mkdir()
        
        # 2. Create source code with WDP markers
        src_file = project_dir / "payment.js"
        src_file.write_text('''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    console.log("Processing payment...");
    return { success: true, transactionId: "txn_123" };
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}
// @wd: utils | END
''')
        
        # 3. Parse the project
        marks = WDPParser.parse_project(str(project_dir), extensions=[".js"])
        
        assert len(marks) == 2
        module_ids = {m.module_id for m in marks}
        assert "payment-core" in module_ids
        assert "utils" in module_ids
        
        # 4. Try to modify safely (only AUDIT module)
        modified_file = project_dir / "payment_modified.js"
        modified_file.write_text('''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    console.log("Processing payment...");
    return { success: true, transactionId: "txn_123" };
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
// @wd-note: Updated for multi-currency support
function formatCurrency(amount, currency = "USD") {
    const symbols = { USD: "$", EUR: "€", GBP: "£" };
    return (symbols[currency] || "$") + amount.toFixed(2);
}
// @wd: utils | END
''')
        
        # 5. Verify the changes
        result = WDPVerifier.verify(marks, str(modified_file))
        
        assert result.ok is True
        assert len(result.violations) == 0
        
        # 6. Try to violate (modify FREEZE module)
        violated_file = project_dir / "payment_violated.js"
        violated_file.write_text('''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    console.log("Processing payment with discount...");  // Changed
    return { success: true, transactionId: "txn_456", discounted: true };  // Changed
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}
// @wd: utils | END
''')
        
        # 7. Verify the violation is caught
        result = WDPVerifier.verify(marks, str(violated_file))
        
        assert result.ok is False
        assert len(result.violations) >= 1

    def test_multiple_files(self, temp_dir):
        """Test WatchDoc with multiple files."""
        project_dir = temp_dir / "multifile"
        project_dir.mkdir()
        
        # File 1: Payment processing
        (project_dir / "payment.js").write_text('''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment
function processPayment(amount, cardInfo) {
    return { success: true };
}
// @wd: payment-core | END
''')
        
        # File 2: User authentication
        (project_dir / "auth.js").write_text('''// @wd: auth-core | Role: Core | Guard: FREEZE | Entry: authenticateUser
function authenticateUser(username, password) {
    return { authenticated: true };
}
// @wd: auth-core | END
''')
        
        # File 3: Utilities
        (project_dir / "utils.js").write_text('''// @wd: string-utils | Role: Util | Guard: AUDIT | Entry: sanitizeInput
function sanitizeInput(input) {
    return input.trim();
}
// @wd: string-utils | END
''')
        
        # Parse all files
        marks = WDPParser.parse_project(str(project_dir), extensions=[".js"])
        
        assert len(marks) == 3
        module_ids = {m.module_id for m in marks}
        assert module_ids == {"payment-core", "auth-core", "string-utils"}

    def test_mixed_languages(self, temp_dir):
        """Test WatchDoc with multiple programming languages."""
        project_dir = temp_dir / "mixed"
        project_dir.mkdir()
        
        # JavaScript
        (project_dir / "payment.js").write_text('''// @wd: payment-js | Role: Core | Guard: FREEZE | Entry: processPayment
function processPayment(amount) {
    return { success: true };
}
// @wd: payment-js | END
''')
        
        # Python
        (project_dir / "payment.py").write_text('''# @wd: payment-py | Role: Core | Guard: FREEZE | Entry: process_payment
def process_payment(amount):
    return {"success": True}
# @wd: payment-py | END
''')
        
        # Parse both
        marks = WDPParser.parse_project(str(project_dir), extensions=[".js", ".py"])
        
        # Should find both marks
        module_ids = {m.module_id for m in marks}
        assert "payment-js" in module_ids
        assert "payment-py" in module_ids
