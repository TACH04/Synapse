"""
Quick verification script to check if dependencies are correctly installed.
Run this with: python check_deps.py
"""

import sys

print("=" * 60)
print("DEPENDENCY VERIFICATION")
print("=" * 60)
print()

# Check Python version
print(f"✓ Python: {sys.version}")
print()

# Check NumPy
try:
    import numpy
    version = numpy.__version__
    if version.startswith("1.26"):
        print(f"✅ NumPy: {version} (CORRECT)")
    elif version.startswith("2."):
        print(f"❌ NumPy: {version} (WRONG - should be 1.26.x)")
    else:
        print(f"⚠️  NumPy: {version} (unexpected version)")
except ImportError:
    print("❌ NumPy: NOT INSTALLED")

# Check PyTorch
try:
    import torch
    version = torch.__version__
    if "+cu" in version:
        print(f"✅ PyTorch: {version} (CUDA version)")
    else:
        print(f"❌ PyTorch: {version} (CPU-only - missing CUDA!)")

    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✅ CUDA Available: True")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    else:
        print(f"❌ CUDA Available: False")
except ImportError:
    print("❌ PyTorch: NOT INSTALLED")

# Check TorchAudio
try:
    import torchaudio
    version = torchaudio.__version__
    if "+cu" in version:
        print(f"✅ TorchAudio: {version} (CUDA version)")
    else:
        print(f"❌ TorchAudio: {version} (CPU-only - missing CUDA!)")
except ImportError:
    print("❌ TorchAudio: NOT INSTALLED")

# Check huggingface-hub
try:
    import huggingface_hub
    version = huggingface_hub.__version__
    major = int(version.split('.')[0])
    if major < 1:
        print(f"✅ huggingface-hub: {version} (CORRECT)")
    else:
        print(f"❌ huggingface-hub: {version} (WRONG - should be < 1.0)")
except ImportError:
    print("❌ huggingface-hub: NOT INSTALLED")

# Check pyannote.audio
try:
    import pyannote.audio
    print(f"✅ pyannote.audio: installed")
except ImportError:
    print("❌ pyannote.audio: NOT INSTALLED")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

# Determine overall status
try:
    import numpy, torch, torchaudio
    if (numpy.__version__.startswith("1.26") and
        "+cu" in torch.__version__ and
        torch.cuda.is_available()):
        print("✅ ALL CRITICAL DEPENDENCIES ARE CORRECT!")
        print()
        print("You can now run the pipeline:")
        print('  python main.py -i "data\\input\\test_audio2.mp3"')
    else:
        print("❌ SOME DEPENDENCIES ARE INCORRECT")
        print()
        print("Please run the fix script:")
        print("  fix_dependencies.ps1 (PowerShell)")
        print("  fix_dependencies.bat (Command Prompt)")
except Exception as e:
    print(f"❌ CRITICAL DEPENDENCIES MISSING")
    print()
    print("Please run the fix script:")
    print("  fix_dependencies.ps1 (PowerShell)")
    print("  fix_dependencies.bat (Command Prompt)")

print("=" * 60)

