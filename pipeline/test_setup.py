#!/usr/bin/env python3
"""
Quick setup test for TechPulse Pipeline
Verifies dependencies and configuration
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import feedparser
        print("  ✓ feedparser")
    except ImportError:
        print("  ✗ feedparser - run: pip install feedparser")
        return False
    
    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        print("  ✗ requests - run: pip install requests")
        return False
    
    try:
        import yaml
        print("  ✓ pyyaml")
    except ImportError:
        print("  ✗ pyyaml - run: pip install pyyaml")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("  ✓ beautifulsoup4")
    except ImportError:
        print("  ✗ beautifulsoup4 - run: pip install beautifulsoup4")
        return False
    
    try:
        import dateutil
        print("  ✓ python-dateutil")
    except ImportError:
        print("  ✗ python-dateutil - run: pip install python-dateutil")
        return False
    
    return True

def test_files():
    """Test that required files exist"""
    print("\nChecking files...")
    
    required_files = [
        "config.yaml",
        "ingestion/sources.yaml",
        "ingestion/rss_fetcher.py",
        "processing/deduplicator.py",
        "output/json_generator.py"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - missing!")
            all_exist = False
    
    return all_exist

def test_directories():
    """Test that output directories exist or can be created"""
    print("\nChecking directories...")
    
    content_dir = Path(__file__).parent.parent / "content"
    
    try:
        content_dir.mkdir(exist_ok=True)
        (content_dir / "daily").mkdir(exist_ok=True)
        print(f"  ✓ content directory: {content_dir}")
        return True
    except Exception as e:
        print(f"  ✗ Cannot create content directory: {e}")
        return False

def test_config():
    """Test that config files are valid"""
    print("\nTesting configuration...")
    
    try:
        import yaml
        
        # Test main config
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("  ✓ config.yaml is valid")
        
        # Test sources config
        sources_path = Path(__file__).parent / "ingestion" / "sources.yaml"
        with open(sources_path, 'r') as f:
            sources = yaml.safe_load(f)
        
        source_count = len(sources.get('sources', []))
        print(f"  ✓ sources.yaml is valid ({source_count} sources configured)")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("TechPulse Pipeline Setup Test")
    print("="*60)
    print()
    
    tests = [
        ("Dependencies", test_imports),
        ("Files", test_files),
        ("Directories", test_directories),
        ("Configuration", test_config)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All tests passed! Ready to run the pipeline.")
        print("\nNext step: python run_pipeline.py")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
