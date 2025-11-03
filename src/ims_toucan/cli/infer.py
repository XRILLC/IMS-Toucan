"""Batch inference CLI for IMS-Toucan."""

import sys
from pathlib import Path


def main():
    """Batch inference entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="IMS-Toucan Batch Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a text file
  toucan-infer --input texts.txt --output-dir outputs/ --language eng

  # Process JSON file with metadata
  toucan-infer --input manifest.json --output-dir outputs/

  # Use custom voice
  toucan-infer --input texts.txt --reference voice.wav --output-dir outputs/
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input file (.txt with one text per line, or .json with metadata)"
    )

    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("outputs"),
        help="Output directory for audio files"
    )

    parser.add_argument(
        "--language", "-l",
        type=str,
        default="eng",
        help="Language code (ISO 639-3)"
    )

    parser.add_argument(
        "--reference", "-r",
        type=Path,
        help="Reference audio for voice cloning"
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to use"
    )

    parser.add_argument(
        "--model",
        type=Path,
        help="Path to custom model checkpoint"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for processing"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load input
    if args.input.suffix == ".json":
        with open(args.input) as f:
            data = json.load(f)
        texts = [item["text"] for item in data]
        output_names = [item.get("output", f"audio_{i:04d}.wav") for i, item in enumerate(data)]
    else:
        with open(args.input) as f:
            texts = [line.strip() for line in f if line.strip()]
        output_names = [f"audio_{i:04d}.wav" for i in range(len(texts))]

    if args.verbose:
        print(f"Loaded {len(texts)} texts from {args.input}")

    # Import and initialize TTS
    try:
        from InferenceInterfaces.ToucanTTSInterface import ToucanTTSInterface
        from tqdm import tqdm
    except ImportError as e:
        print(f"Error: Failed to import dependencies: {e}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"Initializing ToucanTTS (device: {args.device})")

    try:
        tts = ToucanTTSInterface(
            device=args.device,
            language=args.language,
            tts_model_path=str(args.model) if args.model else None
        )

        if args.reference:
            tts.set_utterance_embedding(str(args.reference))

    except Exception as e:
        print(f"Error initializing TTS: {e}", file=sys.stderr)
        return 1

    # Process texts
    success_count = 0
    for text, output_name in tqdm(zip(texts, output_names), total=len(texts), desc="Synthesizing"):
        output_path = args.output_dir / output_name
        try:
            tts.read_to_file(
                text_list=[text],
                file_location=str(output_path)
            )
            success_count += 1
        except Exception as e:
            print(f"Error processing '{text[:30]}...': {e}", file=sys.stderr)

    print(f"\n✓ Successfully generated {success_count}/{len(texts)} audio files")
    print(f"  Output directory: {args.output_dir}")
    return 0 if success_count == len(texts) else 1


if __name__ == "__main__":
    sys.exit(main())
