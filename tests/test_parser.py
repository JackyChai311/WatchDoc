"""
Unit tests for WDPParser.
"""
import pytest
from watchdoc.wdp.parser import WDPParser, WatchdocMark, GuardLevel, RoleType, AssertRule


class TestWDPParser:
    """Test cases for WDPParser."""

    def test_parse_line_basic(self):
        """Test parsing a basic @wd line."""
        line = '// @wd: payment-core | Role: Core | Guard: FREEZE | Entry: processPayment | Summary: "Core payment logic"'
        mark = WDPParser.parse_line(line, 1, "test.js")
        
        assert mark is not None
        assert mark.module_id == "payment-core"
        assert mark.role == RoleType.CORE
        assert mark.guard == GuardLevel.FREEZE
        assert mark.entry == "processPayment"
        assert mark.summary == "Core payment logic"
        assert mark.line_start == 1

    def test_parse_line_missing_fields(self):
        """Test parsing with missing required fields."""
        line = '// @wd: payment-core | Entry: processPayment'
        mark = WDPParser.parse_line(line, 1, "test.js")
        
        assert mark is None

    def test_parse_line_end_marker(self):
        """Test that END markers are not parsed as marks."""
        line = '// @wd: payment-core | END'
        mark = WDPParser.parse_line(line, 10, "test.js")
        
        assert mark is None

    def test_parse_assert_rule(self):
        """Test parsing assertion rules."""
        rule = AssertRule.parse("Signature_Lock")
        assert rule is not None
        assert rule.rule_type == "Signature_Lock"
        assert rule.params == {}

        rule_with_param = AssertRule.parse("Complexity_Limit:10")
        assert rule_with_param is not None
        assert rule_with_param.rule_type == "Complexity_Limit"
        assert rule_with_param.params == {"value": "10"}

        rule_with_multiple_params = AssertRule.parse("Test_Linked:test-file:tests/payment.test.js,timeout:30")
        assert rule_with_multiple_params is not None
        assert rule_with_multiple_params.rule_type == "Test_Linked"
        assert rule_with_multiple_params.params == {
            "test-file": "tests/payment.test.js",
            "timeout": "30"
        }

    def test_parse_file(self, temp_dir, sample_wdp_code):
        """Test parsing a complete file."""
        test_file = temp_dir / "test.js"
        test_file.write_text(sample_wdp_code)
        
        marks = WDPParser.parse_file(str(test_file))
        
        assert len(marks) == 2
        
        # Check first mark
        payment_mark = marks[0]
        assert payment_mark.module_id == "payment-core"
        assert payment_mark.role == RoleType.CORE
        assert payment_mark.guard == GuardLevel.FREEZE
        assert payment_mark.entry == "processPayment"
        assert len(payment_mark.asserts) == 1
        assert payment_mark.asserts[0].rule_type == "Signature_Lock"
        assert payment_mark.line_start == 1
        assert payment_mark.line_end == 7
        
        # Check second mark
        utils_mark = marks[1]
        assert utils_mark.module_id == "utils"
        assert utils_mark.role == RoleType.UTIL
        assert utils_mark.guard == GuardLevel.AUDIT

    def test_mark_to_dict_and_from_dict(self):
        """Test serialization and deserialization of WatchdocMark."""
        mark = WatchdocMark(
            module_id="test-module",
            role=RoleType.CORE,
            guard=GuardLevel.FREEZE,
            entry="testFunction",
            summary="Test summary",
            file_path="test.js",
            line_start=1,
            line_end=10,
            asserts=[AssertRule("Signature_Lock", {})]
        )
        
        # Convert to dict
        mark_dict = mark.to_dict()
        
        assert mark_dict["module_id"] == "test-module"
        assert mark_dict["role"] == "Core"
        assert mark_dict["guard"] == "FREEZE"
        assert mark_dict["entry"] == "testFunction"
        
        # Convert back from dict
        restored_mark = WatchdocMark.from_dict(mark_dict)
        
        assert restored_mark.module_id == mark.module_id
        assert restored_mark.role == mark.role
        assert restored_mark.guard == mark.guard
        assert restored_mark.entry == mark.entry
        assert restored_mark.summary == mark.summary

    def test_parse_project(self, temp_dir, sample_wdp_code, sample_python_code):
        """Test parsing an entire project."""
        # Create test files
        (temp_dir / "test.js").write_text(sample_wdp_code)
        (temp_dir / "test.py").write_text(sample_python_code)
        
        # Create a subdirectory with another file
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "another.js").write_text(sample_wdp_code)
        
        # Parse project
        marks = WDPParser.parse_project(str(temp_dir), extensions=[".js", ".py"])
        
        # Should find marks in all .js and .py files
        assert len(marks) >= 4  # 2 in test.js, 2 in test.py, 2 in subdir/another.js


class TestGuardLevel:
    """Test cases for GuardLevel enum."""

    def test_guard_level_values(self):
        """Test that all guard levels exist."""
        assert GuardLevel.FREEZE.value == "FREEZE"
        assert GuardLevel.GUARD.value == "GUARD"
        assert GuardLevel.AUDIT.value == "AUDIT"
        assert GuardLevel.NONE.value == "NONE"

    def test_guard_level_from_string(self):
        """Test creating GuardLevel from string."""
        assert GuardLevel("FREEZE") == GuardLevel.FREEZE
        assert GuardLevel("GUARD") == GuardLevel.GUARD


class TestRoleType:
    """Test cases for RoleType enum."""

    def test_role_type_values(self):
        """Test that all role types exist."""
        assert RoleType.CORE.value == "Core"
        assert RoleType.UTIL.value == "Util"
        assert RoleType.INTERFACE.value == "Interface"
        assert RoleType.CONFIG.value == "Config"
        assert RoleType.LEGACY.value == "Legacy"

    def test_role_type_from_string(self):
        """Test creating RoleType from string."""
        assert RoleType("Core") == RoleType.CORE
        assert RoleType("Util") == RoleType.UTIL
