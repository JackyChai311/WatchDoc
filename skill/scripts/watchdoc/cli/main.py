#!/usr/bin/env python3
"""
WATCHDOC CLI - Command Line Entry Point
"""

import argparse
import json
import sys
from pathlib import Path
from ..wdp.parser import WDPParser, GuardLevel
from ..wdp.auto_marker import AutoMarker
from ..wgw.manifest import ManifestManager
from ..index.analyzer import ImpactAnalyzer
from ..wgw.override import OverrideManager, OverrideScope, ApprovalLevel
from ..wgw.temporary_grant import TemporaryGrantManager, cmd_grant, cmd_revoke, cmd_session_status

# Import pre-commit verifier
try:
    from ..hooks.pre_commit import PreCommitVerifier
    HAS_PRE_COMMIT = True
except ImportError:
    HAS_PRE_COMMIT = False

def cmd_init(args):
    """Initialize project with auto-scanning"""
    if args.auto_freeze:
        marker = AutoMarker(args.project)
        results = marker.scan_and_mark_all(default_guard=GuardLevel.FREEZE)
        
        print(f"\n✅ Auto-marking complete!")
        print(f"   - Files scanned: {results['total_files']}")
        print(f"   - Functions marked: {results['total_functions']}")
        
        if results.get('language_stats'):
            print(f"\n📊 Language breakdown:")
            for lang, count in sorted(results['language_stats'].items()):
                print(f"   - {lang}: {count} functions")
        
        if results['errors']:
            print(f"\n⚠️  Errors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
    
    manager = ManifestManager(args.project)
    marks = WDPParser.parse_project(args.project)
    manager.sync_from_marks(marks)
    print(f"\n✅ Initialization complete: {len(marks)} modules indexed")

def cmd_scan(args):
    """Scan project for impact analysis"""
    analyzer = ImpactAnalyzer(args.project)
    analyzer.index_project()
    result = analyzer.analyze(args.intent)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_override(args):
    """Create override request"""
    manager = OverrideManager()
    scope = OverrideScope(type=args.scope_type, pattern=args.pattern)
    request = manager.create_request(
        requester_id=args.user_id,
        requester_email=args.email,
        scope=scope,
        reason=args.reason,
        approval_level=ApprovalLevel(args.level),
        duration_hours=args.hours
    )
    print(f"Override request created: {request.request_id}")

def cmd_approve(args):
    """Approve override request"""
    manager = OverrideManager()
    success = manager.submit_approval(
        request_id=args.request_id,
        approver_id=args.user_id,
        approver_email=args.email,
        decision=args.decision,
        comment=args.comment
    )
    print(f"Approval {'successful' if success else 'failed'}")

def cmd_drift(args):
    """Detect drift between code and index"""
    manager = ManifestManager(args.project)
    drift = manager.check_drift()
    
    if drift["has_drift"]:
        print("⚠️  Drift detected!")
        if drift["new_modules"]:
            print(f"\nNew modules: {len(drift['new_modules'])}")
            for module_id in drift["new_modules"]:
                print(f"  + {module_id}")
        
        if drift["removed_modules"]:
            print(f"\nRemoved modules: {len(drift['removed_modules'])}")
            for module_id in drift["removed_modules"]:
                print(f"  - {module_id}")
        
        if drift["modified_hashes"]:
            print(f"\nModified content: {len(drift['modified_hashes'])}")
            for item in drift["modified_hashes"]:
                print(f"  * {item['module_id']}")
        
        if drift["line_changes"]:
            print(f"\nLine number changes: {len(drift['line_changes'])}")
            for item in drift["line_changes"]:
                print(f"  ~ {item['module_id']}: {item['old_lines']} → {item['new_lines']}")
    else:
        print("✅ No drift detected")

def cmd_reindex(args):
    """Reindex the project"""
    manager = ManifestManager(args.project)
    count = manager.reindex()
    print(f"Reindex complete: {count} modules")

def cmd_verify(args):
    """Verify project for WDP compliance"""
    if not HAS_PRE_COMMIT:
        print("❌ Pre-commit verification not available")
        print("   Make sure watchdoc.hooks.pre_commit is installed")
        sys.exit(1)
    
    verifier = PreCommitVerifier(args.project)
    passed = verifier.verify_all()
    verifier.print_report()
    
    if not passed:
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="WATCHDOC CLI")
    subparsers = parser.add_subparsers(dest='command')
 
    init_parser = subparsers.add_parser('init', help='Initialize project')
    init_parser.add_argument('project', help='Project path')
    init_parser.add_argument('--auto-freeze', '-a', action='store_true', 
                            help='Automatically mark all functions as FREEZE')
    init_parser.set_defaults(func=cmd_init)
 
    scan_parser = subparsers.add_parser('scan', help='Scan for impact analysis')
    scan_parser.add_argument('project', help='Project path')
    scan_parser.add_argument('--intent', '-i', required=True, help='Modification intent')
    scan_parser.set_defaults(func=cmd_scan)
 
    override_parser = subparsers.add_parser('override', help='Create override request')
    override_parser.add_argument('--user-id', required=True)
    override_parser.add_argument('--email', required=True)
    override_parser.add_argument('--scope-type', choices=['function', 'module', 'directory'])
    override_parser.add_argument('--pattern', required=True)
    override_parser.add_argument('--reason', required=True)
    override_parser.add_argument('--level', choices=['single', 'dual', 'admin'], default='single')
    override_parser.add_argument('--hours', type=int, default=24)
    override_parser.set_defaults(func=cmd_override)
 
    approve_parser = subparsers.add_parser('approve', help='Approve override request')
    approve_parser.add_argument('--request-id', required=True)
    approve_parser.add_argument('--user-id', required=True)
    approve_parser.add_argument('--email', required=True)
    approve_parser.add_argument('--decision', choices=['approve', 'reject'], required=True)
    approve_parser.add_argument('--comment', default='')
    approve_parser.set_defaults(func=cmd_approve)
 
    drift_parser = subparsers.add_parser('drift', help='Detect drift')
    drift_parser.add_argument('project', help='Project path')
    drift_parser.set_defaults(func=cmd_drift)
 
    reindex_parser = subparsers.add_parser('reindex', help='Reindex project')
    reindex_parser.add_argument('project', help='Project path')
    reindex_parser.set_defaults(func=cmd_reindex)
    
    # Temporary authorization commands
    grant_parser = subparsers.add_parser('grant', help='Grant temporary authorization')
    grant_parser.add_argument('project', help='Project path')
    grant_parser.add_argument('--module-id', required=True, help='Module ID')
    grant_parser.add_argument('--level', required=True, choices=['AUDIT', 'GUARD', 'NONE'], help='Temporary authorization level')
    grant_parser.add_argument('--reason', required=True, help='Authorization reason')
    grant_parser.add_argument('--topic', default='', help='Modification topic')
    grant_parser.set_defaults(func=cmd_grant)
    
    revoke_parser = subparsers.add_parser('revoke', help='Revoke temporary authorization')
    revoke_parser.add_argument('project', help='Project path')
    revoke_parser.add_argument('--module-id', help='Module ID (revoke all if not specified)')
    revoke_parser.set_defaults(func=cmd_revoke)
    
    session_parser = subparsers.add_parser('session', help='View session status')
    session_parser.add_argument('project', help='Project path')
    session_parser.set_defaults(func=cmd_session_status)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify WDP compliance')
    verify_parser.add_argument('project', help='Project path')
    verify_parser.add_argument('--file', '-f', help='Verify specific file only')
    verify_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    verify_parser.set_defaults(func=cmd_verify)
    
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
