#!/usr/bin/env python3
"""
Environment Validation Script for Vocal Feature Analysis Module
================================================================
This script validates that all requirements for Phase 1 are properly installed.

Usage:
    python validate_environment.py
"""

import sys
import os
import subprocess
from importlib import import_module

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_check(check_name, status, message=""):
    """Print a check result."""
    icon = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    print(f"  [{icon}] {check_name}: {status_text}")
    if message:
        print(f"      {message}")

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 10
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_check(
        "Python Version",
        is_valid,
        f"Detected: {version_str} (Required: 3.10+)"
    )
    return is_valid

def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print_check(package_name, True, f"Version: {version}")
        return True
    except ImportError:
        print_check(package_name, False, "Not installed")
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Extract version from first line
            first_line = result.stdout.split('\n')[0]
            print_check("ffmpeg", True, first_line)
            return True
        else:
            print_check("ffmpeg", False, "Command failed")
            return False
    except FileNotFoundError:
        print_check("ffmpeg", False, "Not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print_check("ffmpeg", False, "Command timeout")
        return False

def check_hf_token():
    """Check if Hugging Face token is set."""
    token = os.environ.get("HF_TOKEN")
    
    if token and token.startswith("hf_"):
        masked_token = f"{token[:7]}...{token[-4:]}"
        print_check("HF_TOKEN", True, f"Set: {masked_token}")
        return True
    elif token:
        print_check("HF_TOKEN", False, "Set but doesn't start with 'hf_'")
        return False
    else:
        print_check("HF_TOKEN", False, "Not set - see SETUP.md for instructions")
        return False

def check_cuda():
    """Check if CUDA is available for PyTorch."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print_check(
                "CUDA Support",
                True,
                f"{device_count} device(s) - {device_name}"
            )
        else:
            print_check(
                "CUDA Support",
                False,
                "Not available (CPU mode will be used)"
            )
        
        return cuda_available
    except ImportError:
        print_check("CUDA Support", False, "PyTorch not installed")
        return False

def main():
    """Run all validation checks."""
    print_header("Vocal Feature Analysis - Environment Validation")
    
    all_passed = True
    
    # Check Python version
    print_header("Python Environment")
    all_passed &= check_python_version()
    
    # Check system dependencies
    print_header("System Dependencies")
    all_passed &= check_ffmpeg()
    
    # Check environment variables
    print_header("Environment Variables")
    all_passed &= check_hf_token()
    
    # Check core packages
    print_header("Core Packages")
    core_packages = [
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
    ]
    
    for package_name, import_name in core_packages:
        all_passed &= check_package(package_name, import_name)
    
    # Check audio processing packages
    print_header("Audio Processing Packages")
    audio_packages = [
        ("pyannote.audio", "pyannote.audio"),
        ("openai-whisper", "whisper"),
        ("transformers", "transformers"),
        ("soundfile", "soundfile"),
        ("noisereduce", "noisereduce"),
    ]
    
    for package_name, import_name in audio_packages:
        all_passed &= check_package(package_name, import_name)
    
    # Check data handling packages
    print_header("Data Handling Packages")
    data_packages = [
        ("pandas", "pandas"),
        ("huggingface_hub", "huggingface_hub"),
        ("langdetect", "langdetect"),
    ]
    
    for package_name, import_name in data_packages:
        all_passed &= check_package(package_name, import_name)
    
    # Check optional packages
    print_header("Optional Packages (for Phase 2)")
    optional_packages = [
        ("librosa", "librosa"),
        ("praat-parselmouth", "parselmouth"),
    ]
    
    for package_name, import_name in optional_packages:
        check_package(package_name, import_name)  # Don't affect overall pass status
    
    # Check CUDA availability
    print_header("GPU Acceleration")
    check_cuda()  # Don't affect overall pass status (optional)
    
    # Print summary
    print_header("Validation Summary")
    
    if all_passed:
        print("\n  ✓ All required checks passed!")
        print("  ✓ Your environment is ready for Phase 1 development.")
        print("\n  Next steps:")
        print("    1. Review DevelopmentPlan.md")
        print("    2. Complete Task 1.2: Data Acquisition & Preparation")
        print("    3. Complete Task 1.3: Literature Review & Feature Selection")
    else:
        print("\n  ✗ Some checks failed.")
        print("  ✗ Please review the errors above and fix them.")
        print("\n  See SETUP.md for detailed installation instructions.")
    
    print("\n" + "=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
