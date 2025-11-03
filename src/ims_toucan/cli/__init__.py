"""Command-line interface for IMS-Toucan."""

import sys
from pathlib import Path


def main():
    """Main entry point for toucan-tts CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="IMS-Toucan: Massively Multilingual Text-to-Speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate speech from text
  toucan-tts --text "Hello world" --output hello.wav --language eng

  # Clone a voice
  toucan-tts --text "Hello" --output out.wav --reference voice.wav --language eng

  # Interactive mode
  toucan-tts --interactive --language deu

  # List supported languages
  toucan-tts --list-languages
        """
    )

    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Text to synthesize"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("output.wav"),
        help="Output audio file path (default: output.wav)"
    )

    parser.add_argument(
        "--language", "-l",
        type=str,
        default="eng",
        help="Language code (ISO 639-3, default: eng)"
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
        help="Device to use (default: cpu)"
    )

    parser.add_argument(
        "--model",
        type=Path,
        help="Path to custom model checkpoint"
    )

    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode (read text from stdin)"
    )

    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List all supported languages and exit"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # List languages and exit
    if args.list_languages:
        from Preprocessing.TextFrontend import get_language_id
        from Utility import language_list
        print("Supported languages:")
        # This would need proper implementation
        print("See Utility/language_list.md for full list of 7000+ languages")
        return 0

    # Validate input
    if not args.interactive and not args.text:
        parser.error("Either --text or --interactive must be specified")

    # Import heavy dependencies only when needed
    try:
        from InferenceInterfaces.ToucanTTSInterface import ToucanTTSInterface
    except ImportError as e:
        print(f"Error: Failed to import ToucanTTS: {e}", file=sys.stderr)
        print("Make sure IMS-Toucan is properly installed.", file=sys.stderr)
        return 1

    # Initialize TTS
    if args.verbose:
        print(f"Initializing ToucanTTS (device: {args.device}, language: {args.language})")

    try:
        tts = ToucanTTSInterface(
            device=args.device,
            language=args.language,
            tts_model_path=str(args.model) if args.model else None
        )
    except Exception as e:
        print(f"Error initializing TTS: {e}", file=sys.stderr)
        return 1

    # Set voice if reference provided
    if args.reference:
        if not args.reference.exists():
            print(f"Error: Reference file not found: {args.reference}", file=sys.stderr)
            return 1
        if args.verbose:
            print(f"Cloning voice from: {args.reference}")
        try:
            tts.set_utterance_embedding(str(args.reference))
        except Exception as e:
            print(f"Error loading reference audio: {e}", file=sys.stderr)
            return 1

    # Interactive mode
    if args.interactive:
        print(f"Interactive mode (language: {args.language})")
        print("Enter text to synthesize (Ctrl+D to exit):")
        counter = 1
        try:
            for line in sys.stdin:
                text = line.strip()
                if not text:
                    continue

                output_path = args.output.parent / f"{args.output.stem}_{counter:04d}{args.output.suffix}"
                if args.verbose:
                    print(f"Synthesizing: {text[:50]}...")

                try:
                    tts.read_to_file(
                        text_list=[text],
                        file_location=str(output_path),
                        duration_scaling_factor=1.0 / args.speed
                    )
                    print(f"✓ Saved to: {output_path}")
                    counter += 1
                except Exception as e:
                    print(f"✗ Error: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nExiting...")
        return 0

    # Single text synthesis
    if args.verbose:
        print(f"Synthesizing: {args.text[:50]}...")

    try:
        tts.read_to_file(
            text_list=[args.text],
            file_location=str(args.output),
            duration_scaling_factor=1.0 / args.speed
        )
        print(f"✓ Audio saved to: {args.output}")
        return 0
    except Exception as e:
        print(f"✗ Error during synthesis: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
