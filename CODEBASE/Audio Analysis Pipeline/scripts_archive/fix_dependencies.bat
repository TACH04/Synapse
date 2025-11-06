@echo off
REM Complete Dependency Fix Script
REM Run this from the Synapse root directory with venv activated

echo === Step 1: Verify Virtual Environment ===
echo Current directory: %CD%
echo.

REM Step 1: Fix NumPy
echo === Step 2: Fixing NumPy ===
pip uninstall numpy -y
pip install "numpy<2.0"
echo.

REM Step 2: Install PyTorch with CUDA 11.8
echo === Step 3: Installing PyTorch with CUDA 11.8 ===
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118
echo.

REM Step 3: Fix huggingface-hub version
echo === Step 4: Fixing huggingface-hub ===
pip install "huggingface-hub<1.0,>=0.34.0"
echo.

REM Step 4: Verify installation
echo === Step 5: Verification ===
python -c "import sys; import numpy; import torch; import torchaudio; print('=== Dependency Check ==='); print(f'Python: {sys.version}'); print(f'NumPy: {numpy.__version__}'); print(f'PyTorch: {torch.__version__}'); print(f'TorchAudio: {torchaudio.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print('\n✅ All imports successful!')"
echo.

echo === Complete! ===
echo.
echo Expected values:
echo   NumPy: 1.26.4
echo   PyTorch: 2.7.1+cu118
echo   TorchAudio: 2.7.1+cu118
echo   CUDA Available: True
echo.
echo You can now run: python main.py -i "data\input\test_audio2.mp3"

pause

