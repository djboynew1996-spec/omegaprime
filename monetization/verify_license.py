#!/usr/bin/env python3
"""
==================================================================================
OMEGA PRIME — License Verifier (CLI Tool)
==================================================================================

Quick license verification from command line.

Usage:
    # Single license
    python verify_license.py "OMEGA-<base64>-<sig>"
    
    # From file
    python verify_license.py --file license.lic
    
    # Batch verify multiple files
    python verify_license.py --batch *.lic
    
    # Show all info (JSON)
    python verify_license.py --json "OMEGA-..."
==================================================================================
"""

import sys
import json
import argparse
from pathlib import Path
from generate_license import validate_license


def format_duration(days: int) -> str:
    """Format days into human-readable duration."""
    if days < 0:
        return "EXPIRED"
    if days == 0:
        return "Less than a day"
    if days < 30:
        return f"{days} days"
    if days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    years = days // 365
    remain = days % 365
    if remain == 0:
        return f"{years} year{'s' if years > 1 else ''}"
    return f"{years} year{'s' if years > 1 else ''} {remain} days"


def verify_and_print(license_key: str, show_json: bool = False) -> bool:
    """Verify and print result. Returns True if valid."""
    result = validate_license(license_key)
    
    if show_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result.get("valid", False)
    
    if result.get("valid"):
        print(f"✅  VALID  | {result['customer_id']:30s} | {result['tier'].upper():10s} | {format_duration(result['remaining_days']):20s}")
    else:
        print(f"❌  INVALID | {result.get('customer_id', '?'):30s} | {result.get('error', 'Unknown error')}")
    
    return result.get("valid", False)


def main():
    parser = argparse.ArgumentParser(
        description="🔑 OMEGA PRIME License Verifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("license", nargs="?", help="License key string")
    parser.add_argument("-f", "--file", help="License file to verify")
    parser.add_argument("--batch", help="Glob pattern for batch verify (e.g., *.lic)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    licenses_to_check = []
    
    # Collect licenses
    if args.batch:
        import glob
        for f in glob.glob(args.batch):
            licenses_to_check.append(("file", f))
    elif args.file:
        licenses_to_check.append(("file", args.file))
    elif args.license:
        licenses_to_check.append(("key", args.license))
    else:
        # Try reading from stdin (pipe)
        if not sys.stdin.isatty():
            for line in sys.stdin:
                line = line.strip()
                if line:
                    licenses_to_check.append(("key", line))
        else:
            parser.print_help()
            sys.exit(1)
    
    if not licenses_to_check:
        print("❌ No licenses to verify")
        sys.exit(1)
    
    # Verify
    print()
    if not args.json and not args.summary:
        print(f"{'STATUS':10s} | {'CUSTOMER':30s} | {'TIER':10s} | {'REMAINING/DETAILS'}")
        print("-" * 80)
    
    valid_count = 0
    total_count = len(licenses_to_check)
    
    for source_type, source in licenses_to_check:
        if source_type == "file":
            try:
                key = Path(source).read_text().strip()
            except FileNotFoundError:
                print(f"📁  NOT FOUND | File not found: {source}")
                continue
        else:
            key = source
        
        is_valid = verify_and_print(key, show_json=args.json)
        if is_valid:
            valid_count += 1
    
    # Summary
    if not args.json:
        print()
        print("=" * 80)
        print(f"📊  Summary: {valid_count}/{total_count} licenses valid")
        if valid_count == total_count and total_count > 0:
            print("✅  All licenses are valid!")
        elif valid_count < total_count:
            print(f"⚠️  {total_count - valid_count} license(s) need renewal")
        print("=" * 80)
    
    sys.exit(0 if valid_count == total_count else 1)


if __name__ == "__main__":
    main()
