import torch
from pyannote.audio import Pipeline

# Simple test to understand DiarizeOutput structure
HF_TOKEN = "REDACTED"
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

# Create dummy audio
waveform = torch.randn(1, 16000)
result = pipeline({"waveform": waveform, "sample_rate": 16000})

# Write output to file
with open("diarize_structure.txt", "w") as f:
    f.write(f"Type: {type(result)}\n")
    f.write(f"Is tuple: {isinstance(result, tuple)}\n")
    f.write(f"Has _fields: {hasattr(result, '_fields')}\n\n")

    if hasattr(result, '_fields'):
        f.write(f"Fields: {result._fields}\n\n")
        for field in result._fields:
            val = getattr(result, field)
            f.write(f"  {field}: {type(val)}\n")
            if hasattr(val, 'itertracks'):
                f.write(f"    -> Has itertracks method!\n")

    f.write(f"\nAll attributes:\n")
    for attr in dir(result):
        if not attr.startswith('_'):
            f.write(f"  - {attr}\n")

    # Try tuple indexing
    try:
        first = result[0]
        f.write(f"\nresult[0] type: {type(first)}\n")
        f.write(f"Has itertracks: {hasattr(first, 'itertracks')}\n")
    except Exception as e:
        f.write(f"\nCannot index: {e}\n")

print("Output written to diarize_structure.txt")

