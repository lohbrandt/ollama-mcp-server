#!/usr/bin/env python3
"""
Test runner for Ollama MCP Server
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    """Main test runner."""
    print("🧪 Ollama MCP Server Test Runner")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run from project root.")
        sys.exit(1)
    
    # Install test dependencies if needed
    print("\n📦 Checking test dependencies...")
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        if not run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], 
                          "Installing test dependencies"):
            sys.exit(1)
    
    # Run different test categories
    test_results = []
    
    # Unit tests
    test_results.append(
        run_command([sys.executable, "-m", "pytest", "tests/unit/", "-v"], 
                   "Unit Tests")
    )
    
    # Integration tests (skip if Ollama not available)
    test_results.append(
        run_command([sys.executable, "-m", "pytest", "tests/integration/", 
                    "-m", "not ollama_required", "-v"], 
                   "Integration Tests (without Ollama)")
    )
    
    # Code formatting check
    test_results.append(
        run_command([sys.executable, "-m", "black", "--check", "src/", "tests/"], 
                   "Code Formatting Check")
    )
    
    # Type checking
    test_results.append(
        run_command([sys.executable, "-m", "mypy", "src/"], 
                   "Type Checking")
    )
    
    # Linting
    test_results.append(
        run_command([sys.executable, "-m", "flake8", "src/", "tests/"], 
                   "Code Linting")
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print('='*60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 