"""
Main Execution Script for Clinical Audio Analysis Pipeline (Phase 2)
Runs the specialized clinical emotion model after fine-tuning.
"""

import os
import argparse
from pipeline.analysis_pipeline import AnalysisPipeline


def main():
    """
    Main entry point for the Clinical Audio Analysis Pipeline (Phase 2).
    This script demonstrates the "hot-swap" functionality by using the
    fine-tuned clinical emotion model instead of the general-purpose model.
    """
    parser = argparse.ArgumentParser(
        description="Run the Clinical Audio Analysis Pipeline (Phase 2 - Specialized Model).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_phase2.py -i ./data/input/conversation.mp3
  python main_phase2.py -i ./data/input/convo.wav --asr medium.en --speakers 2
  python main_phase2.py -i ./data/input/session.m4a -o ./results/
        """
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        type=str,
        help="Path to the input audio file (.wav, .mp3, .m4a, etc.)"
    )
    parser.add_argument(
        "-o", "--output_dir",
        default="./data/output/",
        type=str,
        help="Directory to save the output JSON (default: ./data/output/)"
    )
    parser.add_argument(
        "--asr",
        default="base.en",
        type=str,
        help="ASR model to use: 'base.en' or 'medium.en' (default: base.en)"
    )
    parser.add_argument(
        "--speakers",
        default=2,
        type=int,
        help="Number of speakers to detect (default: 2)"
    )
    parser.add_argument(
        "--model_path",
        default="./models/clinical_ser_model/",
        type=str,
        help="Path to the fine-tuned clinical emotion model (default: ./models/clinical_ser_model/)"
    )

    args = parser.parse_args()

    # 1. Get Hugging Face Token (Critical)
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token is None:
        print("=" * 60)
        print("ERROR: HF_TOKEN environment variable not set")
        print("=" * 60)
        print("\nThe speaker diarization model requires authentication.")
        print("\nPlease follow these steps:")
        print("1. Visit https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("   and accept the user conditions")
        print("2. Visit https://huggingface.co/settings/tokens")
        print("   and generate a 'read' access token")
        print("3. Set the token as an environment variable:")
        print("\n   Windows (Command Prompt):")
        print("   set HF_TOKEN=your_token_here")
        print("\n   Windows (PowerShell):")
        print("   $env:HF_TOKEN=\"your_token_here\"")
        print("\n   Linux/Mac:")
        print("   export HF_TOKEN=\"your_token_here\"")
        print("\n" + "=" * 60)
        return

    # 2. Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return

    # 3. Validate model exists
    if not os.path.exists(args.model_path):
        print(f"Error: Fine-tuned model not found at {args.model_path}")
        print("\nPlease complete Phase 2 training first:")
        print("1. Run main.py to generate JSON outputs")
        print("2. Run scripts/prepare_dataset.py to create dataset")
        print("3. Label the dataset with clinical emotions")
        print("4. Run scripts/train_emotion_model.py to fine-tune the model")
        return

    # 4. Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # 5. Define output path
    base_filename = os.path.basename(args.input)
    output_filename = os.path.splitext(base_filename)[0] + "_phase2.json"
    output_json_path = os.path.join(args.output_dir, output_filename)

    # 6. Initialize and run the pipeline
    # THIS IS THE HOT-SWAP: We use the fine-tuned clinical model
    try:
        print("\n" + "=" * 60)
        print("PHASE 2: Using Fine-Tuned Clinical Emotion Model")
        print("=" * 60 + "\n")

        pipeline = AnalysisPipeline(
            hf_token=hf_token,
            emotion_model_path=args.model_path,  # <-- THIS IS THE HOT-SWAP
            asr_model=args.asr
        )

        pipeline.run(
            audio_file_path=args.input,
            output_json_path=output_json_path,
            num_speakers=args.speakers
        )
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"An error occurred during pipeline execution:")
        print(f"{'='*60}")
        print(f"{e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

