"""Example: Using IMS-Toucan as a Python library.

This script demonstrates how to use IMS-Toucan as an importable Python library
for text-to-speech synthesis. It generates speech audio from text using the
high-level ToucanTTS interface.

Requirements:
    - IMS-Toucan installed: `uv pip install -e .`
    - CUDA-enabled GPU recommended (CPU works but slower)
    - Internet connection for first run (downloads pretrained models)

Usage:
    python examples/library_usage_example.py

Output:
    Creates three WAV files in the current directory:
    - horse_waffles.wav
    - souffle_climb.wav
    - ruffian_coat.wav
"""

from ims_toucan import ToucanTTS


def main():
    """Generate speech audio for three example sentences."""

    # Initialize TTS interface
    # - device="cpu" for CPU inference, "cuda" for GPU (10x+ faster)
    # - language="eng" for English text
    # - Models auto-download from Hugging Face on first run
    print("Initializing ToucanTTS...")
    tts = ToucanTTS(device="cpu", language="eng")
    print("✓ ToucanTTS initialized\n")

    # Define test sentences
    test_cases = [
        {
            "text": "My horse is enamored of eating waffles",
            "output": "horse_waffles.wav",
            "description": "Testing unusual word combinations and multi-syllabic words"
        },
        {
            "text": "A nice souffle is hard to climb with",
            "output": "souffle_climb.wav",
            "description": "Testing French loanword pronunciation and absurdist phrasing"
        },
        {
            "text": "A ruffian stole my coat",
            "output": "ruffian_coat.wav",
            "description": "Testing archaic vocabulary and simple narrative"
        }
    ]

    # Generate speech for each test case
    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/3] Generating: \"{test['text']}\"")
        print(f"       Purpose: {test['description']}")

        # Synthesize speech to file
        # - text_list: List of sentences to synthesize
        # - file_location: Output WAV file path
        # - duration_scaling_factor: Speed control (1.0 = normal, <1.0 = faster, >1.0 = slower)
        tts.read_to_file(
            text_list=[test["text"]],
            file_location=test["output"],
            duration_scaling_factor=1.0
        )

        print(f"       ✓ Saved to {test['output']}\n")

    print("=" * 60)
    print("All audio files generated successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    for test in test_cases:
        print(f"  - {test['output']}")

    print("\nYou can play these files with:")
    print("  - Command line: aplay horse_waffles.wav")
    print("  - GUI: Open in any audio player")
    print("  - Python: Use sounddevice, pygame, or similar libraries")


if __name__ == "__main__":
    main()
