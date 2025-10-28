import torch
import torchaudio
from pyannote.audio import Pipeline

# Create a simple test audio
dummy_waveform = torch.randn(1, 16000)

# Load the pipeline
HF_TOKEN = "REDACTED"
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

# Run diarization
result = pipeline({"waveform": dummy_waveform, "sample_rate": 16000})

# Check the type and available methods
print(f"Result type: {type(result)}")
print(f"Result dir: {[m for m in dir(result) if not m.startswith('_')]}")

# Try to understand the structure
print(f"\nResult content: {result}")

