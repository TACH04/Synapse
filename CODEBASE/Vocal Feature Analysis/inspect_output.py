import torch
import torchaudio
from pyannote.audio import Pipeline

# Load a small test audio
waveform = torch.randn(1, 16000)

# Load the pipeline
HF_TOKEN = "REDACTED"
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

# Run diarization
result = pipeline({"waveform": waveform, "sample_rate": 16000})

# Inspect the result
print(f"Result type: {type(result)}")
print(f"\nAvailable attributes:")
for attr in dir(result):
    if not attr.startswith('_'):
        print(f"  - {attr}")

print(f"\nResult fields (if NamedTuple): {result._fields if hasattr(result, '_fields') else 'Not a NamedTuple'}")

# Try to print the result
print(f"\nResult content:\n{result}")

# Check if it has specific attributes
if hasattr(result, 'segments'):
    print(f"\nHas 'segments' attribute")
if hasattr(result, 'speaker_diarization'):
    print(f"\nHas 'speaker_diarization' attribute")
    print(f"Type: {type(result.speaker_diarization)}")

