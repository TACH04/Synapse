"""
Audio Conversion Script
Converts audio files to 16kHz mono WAV format for the VocalAnalysis pipeline.
Supports: M4A, MP3, AAC, OGG, FLAC, and other common formats.

Usage:
    python convert_audio.py input_file.m4a [output_file.wav]
"""

import sys
import os
import subprocess

def convert_to_wav(input_path, output_path=None):
    """
    Convert an audio file to 16kHz mono WAV format.

    Args:
        input_path (str): Path to the input audio file
        output_path (str, optional): Path for the output WAV file.
                                     If not provided, will use input filename with .wav extension

    Returns:
        str: Path to the output WAV file
    """
    # Validate input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted.wav"

    print(f"Converting audio file: {input_path}")

    # Try using ffmpeg directly (more reliable for Python 3.13+)
    try:
        # Check if ffmpeg is available
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Use ffmpeg to convert
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",       # mono (1 channel)
                "-sample_fmt", "s16",  # 16-bit PCM
                "-y",             # overwrite output file
                output_path
            ]

            print("Using ffmpeg for conversion...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise Exception(f"ffmpeg conversion failed: {result.stderr}")

            print(f"✓ Conversion complete!")
            print(f"Output saved to: {output_path}")

            # Display file info
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"File size: {file_size_mb:.2f} MB")

            return output_path

    except FileNotFoundError:
        # ffmpeg not found, try pydub as fallback
        pass

    # Fallback to pydub (for older Python versions)
    try:
        from pydub import AudioSegment

        print(f"Loading audio file: {input_path}")
        audio = AudioSegment.from_file(input_path)

        print(f"Original format: {audio.channels} channel(s), {audio.frame_rate} Hz")

        # Convert to mono (1 channel) and 16kHz sample rate
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        print(f"Converting to: 1 channel, 16000 Hz")

        # Export as WAV
        audio.export(output_path, format="wav")

        print(f"✓ Conversion complete!")
        print(f"Output saved to: {output_path}")

        # Display file info
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        duration_sec = len(audio) / 1000.0
        print(f"Duration: {duration_sec:.2f} seconds")
        print(f"File size: {file_size_mb:.2f} MB")

        return output_path

    except ImportError:
        raise Exception(
            "Neither ffmpeg nor pydub is available for audio conversion.\n"
            "Please install ffmpeg from https://ffmpeg.org/download.html\n"
            "and add it to your system PATH."
        )
    except Exception as e:
        raise Exception(f"Audio conversion failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_audio.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert_audio.py test_audio.m4a")
        print("  python convert_audio.py test_audio.m4a output.wav")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = convert_to_wav(input_file, output_file)
        print(f"\n✓ Ready to use with VocalAnalysis.py: {result}")
    except Exception as e:
        print(f"\n✗ Conversion failed: {e}")
        sys.exit(1)
