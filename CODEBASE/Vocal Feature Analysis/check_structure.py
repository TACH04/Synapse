import torch
from pyannote.audio import Pipeline

# Simple test to understand DiarizeOutput structure
HF_TOKEN = "REDACTED"
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

# Create dummy audio
waveform = torch.randn(1, 16000)
result = pipeline({"waveform": waveform, "sample_rate": 16000})

print(f"Type: {type(result)}")
print(f"\nIs tuple: {isinstance(result, tuple)}")
print(f"Has _fields: {hasattr(result, '_fields')}")

if hasattr(result, '_fields'):
    print(f"Fields: {result._fields}")
    for field in result._fields:
        val = getattr(result, field)
        print(f"  {field}: {type(val)}")
        if hasattr(val, 'itertracks'):
            print(f"    -> Has itertracks method!")

# Try tuple indexing
try:
    first = result[0]
    print(f"\nresult[0] type: {type(first)}")
    print(f"Has itertracks: {hasattr(first, 'itertracks')}")
except Exception as e:
    print(f"\nCannot index: {e}")

