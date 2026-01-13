"""
Installation Validation Script

Quick check to ensure all sample data files are present and accessible.

Usage:
    python validate_installation.py
"""

import os
import sys

def check_file(filepath, expected_size_kb=None):
    """Check if file exists and optionally verify size"""
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        status = "✓"
        if expected_size_kb and abs(size_kb - expected_size_kb) > expected_size_kb * 0.5:
            status = "⚠"
        print(f"  {status} {os.path.basename(filepath)} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"  ✗ MISSING: {os.path.basename(filepath)}")
        return False


def validate_installation():
    """Validate that all required files are present"""
    print("=" * 70)
    print("CANOPI SAMPLE DATA INSTALLATION VALIDATION")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Check CSV data files
    print("\n1. CSV Data Files:")
    csv_files = [
        'nodes.csv',
        'branches.csv',
        'generators.csv',
        'load_profiles.csv',
        'renewable_profiles_template.csv',
        'generator_costs.csv'
    ]

    csv_ok = all(check_file(os.path.join(base_dir, f)) for f in csv_files)

    # Check Python modules
    print("\n2. Python Modules:")
    loader_dir = os.path.join(base_dir, '..', 'loaders')
    py_files = [
        ('__init__.py', 0.5),
        ('sample_data_loader.py', 10)
    ]

    py_ok = all(check_file(os.path.join(loader_dir, f), size) for f, size in py_files)

    # Check utility scripts
    print("\n3. Utility Scripts:")
    script_files = [
        'generate_renewable_profiles.py',
        'visualize_network.py',
        'test_data_loader.py'
    ]

    scripts_ok = all(check_file(os.path.join(base_dir, f)) for f in script_files)

    # Check documentation
    print("\n4. Documentation:")
    doc_files = [
        'README.md',
        'QUICKSTART.md',
        'FILES_CREATED.md'
    ]

    docs_ok = all(check_file(os.path.join(base_dir, f)) for f in doc_files)

    # Check if can be imported
    print("\n5. Python Import Test:")
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(base_dir, '../..')))
        from data_pipelines.loaders import load_sample_data
        print("  ✓ Module can be imported")
        import_ok = True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import_ok = False

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    results = {
        'CSV Data Files': csv_ok,
        'Python Modules': py_ok,
        'Utility Scripts': scripts_ok,
        'Documentation': docs_ok,
        'Import Test': import_ok
    }

    all_ok = all(results.values())

    for category, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {category}")

    print("\n" + "=" * 70)
    if all_ok:
        print("✓ INSTALLATION VALIDATED SUCCESSFULLY")
        print("\nNext steps:")
        print("  1. Run tests: python test_data_loader.py")
        print("  2. Load data: from data_pipelines.loaders import load_sample_data")
        print("  3. Read docs: README.md and QUICKSTART.md")
    else:
        print("✗ INSTALLATION INCOMPLETE")
        print("\nSome files are missing. Please check the installation.")

    print("=" * 70 + "\n")

    return all_ok


if __name__ == '__main__':
    success = validate_installation()
    sys.exit(0 if success else 1)
