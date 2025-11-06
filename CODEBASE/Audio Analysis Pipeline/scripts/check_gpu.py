"""
GPU Detection and Diagnostic Script
Run this to verify your GPU is available and properly configured for the pipeline.
"""

import sys

def check_gpu():
    """Check GPU availability and configuration."""

    print("=" * 70)
    print("GPU DETECTION AND DIAGNOSTIC REPORT")
    print("=" * 70)

    # 1. Check PyTorch
    print("\n1. Checking PyTorch Installation...")
    try:
        import torch
        print(f"   ✓ PyTorch version: {torch.__version__}")

        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"   ✓ CUDA available: {cuda_available}")

        if cuda_available:
            print(f"   ✓ CUDA version: {torch.version.cuda}")
            print(f"   ✓ cuDNN version: {torch.backends.cudnn.version()}")
            print(f"   ✓ Number of GPUs: {torch.cuda.device_count()}")

            for i in range(torch.cuda.device_count()):
                print(f"\n   GPU {i}:")
                print(f"      Name: {torch.cuda.get_device_name(i)}")
                print(f"      Compute Capability: {torch.cuda.get_device_capability(i)}")

                # Memory info
                mem_total = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                mem_reserved = torch.cuda.memory_reserved(i) / (1024**3)
                mem_allocated = torch.cuda.memory_allocated(i) / (1024**3)

                print(f"      Total Memory: {mem_total:.2f} GB")
                print(f"      Reserved Memory: {mem_reserved:.2f} GB")
                print(f"      Allocated Memory: {mem_allocated:.2f} GB")
        else:
            print("   ⚠ CUDA is not available. Running on CPU only.")
            print("   → Check NVIDIA drivers and CUDA installation")

    except ImportError:
        print("   ✗ PyTorch is not installed")
        print("   → Install with: pip install torch torchvision torchaudio")
        return False

    # 2. Check transformers (for emotion model)
    print("\n2. Checking Transformers Installation...")
    try:
        import transformers
        print(f"   ✓ Transformers version: {transformers.__version__}")
    except ImportError:
        print("   ✗ Transformers is not installed")
        print("   → Install with: pip install transformers")

    # 3. Check faster-whisper (for ASR)
    print("\n3. Checking faster-whisper Installation...")
    try:
        import faster_whisper
        print(f"   ✓ faster-whisper is installed")
    except ImportError:
        print("   ✗ faster-whisper is not installed")
        print("   → Install with: pip install faster-whisper")

    # 4. Check pyannote.audio (for diarization)
    print("\n4. Checking pyannote.audio Installation...")
    try:
        import pyannote.audio
        print(f"   ✓ pyannote.audio version: {pyannote.audio.__version__}")
    except ImportError:
        print("   ✗ pyannote.audio is not installed")
        print("   → Install with: pip install pyannote.audio")

    # 5. Test GPU with simple operation
    if cuda_available:
        print("\n5. Testing GPU with Simple Operation...")
        try:
            # Create a tensor on GPU
            test_tensor = torch.randn(1000, 1000).cuda()
            result = test_tensor @ test_tensor.T
            print("   ✓ GPU computation successful")
            print(f"   ✓ Test tensor shape: {result.shape}")

            # Clean up
            del test_tensor, result
            torch.cuda.empty_cache()

        except Exception as e:
            print(f"   ✗ GPU test failed: {e}")

    # 6. Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if not cuda_available:
        print("\n⚠ GPU NOT DETECTED - Pipeline will run on CPU (slower)")
        print("\nTo enable GPU acceleration:")
        print("1. Install NVIDIA GPU drivers: https://www.nvidia.com/Download/index.aspx")
        print("2. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
        print("3. Install PyTorch with CUDA support:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    else:
        print("\n✓ GPU DETECTED - Pipeline will use GPU acceleration")
        print("\nYour system is configured for optimal performance!")
        print("\nExpected performance:")
        print("  - 20-minute audio file: ~8-12 minutes processing")
        print("  - GPU will be used for:")
        print("    • Speaker diarization (Step 1)")
        print("    • Emotion recognition (Step 2)")
        print("    • Speech transcription (Step 2)")

    print("\n" + "=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    return cuda_available


if __name__ == "__main__":
    gpu_available = check_gpu()
    sys.exit(0 if gpu_available else 1)

