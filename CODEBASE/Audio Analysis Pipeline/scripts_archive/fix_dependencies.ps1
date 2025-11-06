# Complete Dependency Fix Script
# Run this from the Synapse root directory with venv activated

Write-Host "=== Step 1: Verify Virtual Environment ===" -ForegroundColor Cyan
Write-Host "Current directory: $(Get-Location)"
Write-Host ""

# Step 1: Fix NumPy
Write-Host "=== Step 2: Fixing NumPy ===" -ForegroundColor Cyan
pip uninstall numpy -y
pip install "numpy<2.0"
Write-Host ""

# Step 2: Install PyTorch with CUDA 11.8
Write-Host "=== Step 3: Installing PyTorch with CUDA 11.8 ===" -ForegroundColor Cyan
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118
Write-Host ""

# Step 3: Fix huggingface-hub version
Write-Host "=== Step 4: Fixing huggingface-hub ===" -ForegroundColor Cyan
pip install "huggingface-hub<1.0,>=0.34.0"
Write-Host ""

# Step 4: Verify installation
Write-Host "=== Step 5: Verification ===" -ForegroundColor Cyan
python -c @"
import sys
import numpy
import torch
import torchaudio

print('=== Dependency Check ===')
print(f'Python: {sys.version}')
print(f'NumPy: {numpy.__version__}')
print(f'PyTorch: {torch.__version__}')
print(f'TorchAudio: {torchaudio.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
print('\n✅ All imports successful!')
"@

Write-Host ""
Write-Host "=== Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Expected values:"
Write-Host "  NumPy: 1.26.4"
Write-Host "  PyTorch: 2.7.1+cu118"
Write-Host "  TorchAudio: 2.7.1+cu118"
Write-Host "  CUDA Available: True"
Write-Host ""
Write-Host "You can now run: python main.py -i `"data\input\test_audio2.mp3`"" -ForegroundColor Yellow

