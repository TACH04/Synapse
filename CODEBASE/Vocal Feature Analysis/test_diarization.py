import torch
import torchaudio
import os
from pyannote.audio import Pipeline

# Create a simple test audio
dummy_waveform = torch.randn(1, 16000)

# Load the pipeline
HF_TOKEN = os.environ.get("HF_TOKEN", None)
if HF_TOKEN is None:
    print("Error: HF_TOKEN environment variable not set")
    print("Please set it with: export HF_TOKEN='hf_your_token_here'")
    exit(1)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

# Run diarization
result = pipeline({"waveform": dummy_waveform, "sample_rate": 16000})

# Check the type and available methods
print(f"Result type: {type(result)}")
print(f"Result dir: {[m for m in dir(result) if not m.startswith('_')]}")

# Try to understand the structure
print(f"\nResult content: {result}")

