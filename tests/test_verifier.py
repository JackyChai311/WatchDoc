"""
Unit tests for WDPVerifier.
"""
import pytest
import tempfile
from pathlib import Path
from watchdoc.wdp.parser import WDPParser, GuardLevel
from watchdoc.wdp.verifier import WDPVerifier, VerificationResult


class TestVerificationResult:
    """Test cases for VerificationResult."""

    def test_initial_state(self):
        """Test initial state of verification result."""
        result = VerificationResult()
        assert result.ok is True
        assert len(result.violations) == 0
        assert len(result.warnings) == 0
        assert len(result.suggestions) == 0

    def test_add_violation(self):
        """Test adding a violation."""
        result = VerificationResult()
        result.add_violation("Test violation")
        
        assert result.ok is False
        assert len(result.violations) == 1
        assert result.violations[0] == "Test violation"

    def test_add_warning(self):
        """Test adding a warning."""
        result = VerificationResult()
        result.add_warning("Test warning")
        
        assert result.ok is True  # Warnings don't make it fail
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"

    def test_add_suggestion(self):
        """Test adding a suggestion."""
        result = VerificationResult()
        result.add_suggestion("Test suggestion")
        
        assert len(result.suggestions) == 1
        assert result.suggestions[0] == "Test suggestion"

    def test_to_dict(self):
        """Test converting to dictionary."""
        result = VerificationResult()
        result.add_violation("Violation 1")
        result.add_warning("Warning 1")
        result.add_suggestion("Suggestion 1")
        
        result_dict = result.to_dict()
        
        assert result_dict["ok"] is False
        assert len(result_dict["violations"]) == 1
        assert len(result_dict["warnings"]) == 1
        assert len(result_dict["suggestions"]) == 1


class TestWDPVerifier:
    """Test cases for WDPVerifier."""

    @pytest.fixture
    def original_code(self):
        """Original code with WDP markers."""
        return '''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
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
    def modified_code_ok(self):
        """Modified code that is acceptable (only AUDIT module changed)."""
        return '''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    return { success: true, transactionId: "txn_123" };
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
// @wd-note: Updated format to use euros
function formatCurrency(amount) {
    return "€" + amount.toFixed(2);
}
// @wd: utils | END
'''

    @pytest.fixture
    def modified_code_violation(self):
        """Modified code with violation (FREEZE module changed)."""
        return '''// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"
// @wd-assert: Signature_Lock
function processPayment(amount, cardInfo) {
    return { success: true, transactionId: "txn_456" };
}
// @wd: payment-core | END

// @wd: utils | Role: Util | Guard: AUDIT | Summary: "Utility functions"
function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}
// @wd: utils | END
'''

    def test_verify_no_changes(self, temp_dir, original_code):
        """Test verification when no changes are made."""
        # Write original code
        orig_file = temp_dir / "original.js"
        orig_file.write_text(original_code)
        
        # Parse original marks
        original_marks = WDPParser.parse_file(str(orig_file))
        
        # Verify with same code
        result = WDPVerifier.verify(original_marks, str(orig_file))
        
        assert result.ok is True
        assert len(result.violations) == 0

    def test_verify_audit_change_with_note(self, temp_dir, original_code, modified_code_ok):
        """Test verification when AUDIT module is changed with note."""
        # Write original and modified code
        orig_file = temp_dir / "original.js"
        orig_file.write_text(original_code)
        
        modified_file = temp_dir / "modified.js"
        modified_file.write_text(modified_code_ok)
        
        # Parse original marks
        original_marks = WDPParser.parse_file(str(orig_file))
        
        # Verify
        result = WDPVerifier.verify(original_marks, str(modified_file))
        
        assert result.ok is True
        assert len(result.violations) == 0

    def test_verify_freeze_violation(self, temp_dir, original_code, modified_code_violation):
        """Test verification when FREEZE module is changed."""
        # Write original and modified code
        orig_file = temp_dir / "original.js"
        orig_file.write_text(original_code)
        
        modified_file = temp_dir / "modified.js"
        modified_file.write_text(modified_code_violation)
        
        # Parse original marks
        original_marks = WDPParser.parse_file(str(orig_file))
        
        # Verify
        result = WDPVerifier.verify(original_marks, str(modified_file))
        
        assert result.ok is False
        assert len(result.violations) >= 1
        assert any("FREEZE violation" in v for v in result.violations)

    def test_verify_with_authorization(self, temp_dir, original_code, modified_code_violation):
        """Test verification with temporary authorization."""
        # Write original and modified code
        orig_file = temp_dir / "original.js"
        orig_file.write_text(original_code)
        
        modified_file = temp_dir / "modified.js"
        modified_file.write_text(modified_code_violation)
        
        # Parse original marks
        original_marks = WDPParser.parse_file(str(orig_file))
        
        # Verify with authorization (score > 1 allows modification)
        result = WDPVerifier.verify(
            original_marks, 
            str(modified_file),
            authorizations={"payment-core": 2}  # Authorized
        )
        
        # With authorization, even FREEZE module can be modified
        assert result.ok is True or len(result.violations) == 0

    def test_verify_hash(self):
        """Test hash verification."""
        code = "function test() { return 42; }"
        expected_hash = WDPVerifier.verify_hash("", code)  # First get a hash
        
        # Now verify with same code
        code_hash = WDPVerifier.verify_hash("", code)
        result = WDPVerifier.verify_hash(code_hash, code)
        
        assert result is True
        
        # Verify with different code
        different_code = "function test() { return 43; }"
        result = WDPVerifier.verify_hash(code_hash, different_code)
        
        assert result is False
