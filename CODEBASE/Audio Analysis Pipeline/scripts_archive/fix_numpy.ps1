# NumPy Compatibility Fix Script
# This script fixes the NumPy 2.x compatibility issue with pyannote.audio

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "NumPy Compatibility Fix for Clinical Audio Analysis Pipeline" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

Write-Host "Issue: pyannote.audio is not compatible with NumPy 2.x" -ForegroundColor Red
Write-Host "Fix: Downgrade to NumPy 1.x (1.26.x)" -ForegroundColor Green
Write-Host ""

# Step 1: Uninstall NumPy 2.x
Write-Host "Step 1: Uninstalling NumPy 2.x..." -ForegroundColor Yellow
pip uninstall numpy -y

# Step 2: Install NumPy 1.x
Write-Host "`nStep 2: Installing NumPy 1.x..." -ForegroundColor Yellow
pip install "numpy<2.0"

# Step 3: Verify installation
Write-Host "`nStep 3: Verifying installation..." -ForegroundColor Yellow
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Fix Complete! You can now run:" -ForegroundColor Green
Write-Host "  python main.py -i ./data/input/test_audio.mp3" -ForegroundColor White
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

