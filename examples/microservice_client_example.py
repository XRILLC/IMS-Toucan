"""Example: Using IMS-Toucan as a REST API microservice.

This script demonstrates how to use IMS-Toucan as a REST microservice by making
HTTP requests to the FastAPI server. The service must be running before executing
this script.

Requirements:
    - ToucanTTS microservice running: `toucan-serve --host 127.0.0.1 --port 8000`
    - requests library: `pip install requests`

Usage:
    # Terminal 1: Start the service
    toucan-serve --host 127.0.0.1 --port 8000

    # Terminal 2: Run this client
    python examples/microservice_client_example.py

Output:
    Creates three WAV files in the current directory:
    - spatula_rutabega.wav
    - shoes_edible.wav
    - balloons_purple.wav
"""

import requests
import sys
from pathlib import Path


def check_health(base_url: str = "http://127.0.0.1:8000") -> bool:
    """Check if the TTS service is running and healthy.

    Args:
        base_url: Base URL of the TTS service.

    Returns:
        True if service is healthy, False otherwise.
    """
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service is healthy: {data}")
            return True
        else:
            print(f"✗ Service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to service. Is it running?")
        print("  Start with: toucan-serve --host 127.0.0.1 --port 8000")
        return False
    except Exception as e:
        print(f"✗ Error checking health: {e}")
        return False


def synthesize_speech(text: str,
                     output_file: str,
                     language: str = "eng",
                     speed: float = 1.0,
                     base_url: str = "http://127.0.0.1:8000") -> bool:
    """Synthesize speech from text using the TTS API.

    Args:
        text: Text to synthesize.
        output_file: Path to save the generated WAV file.
        language: ISO 639-3 language code (e.g., "eng", "deu", "cmn").
        speed: Speech speed multiplier (1.0 = normal, <1.0 = faster, >1.0 = slower).
        base_url: Base URL of the TTS service.

    Returns:
        True if synthesis succeeded, False otherwise.
    """
    try:
        # Prepare request payload
        payload = {
            "text": text,
            "language": language,
            "speed": speed
        }

        # Make POST request to synthesize endpoint
        response = requests.post(
            f"{base_url}/synthesize",
            json=payload,
            timeout=30  # Allow time for synthesis
        )

        if response.status_code == 200:
            # Save audio to file
            with open(output_file, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"✗ Synthesis failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("✗ Request timed out. Synthesis may take longer for long texts.")
        return False
    except Exception as e:
        print(f"✗ Error during synthesis: {e}")
        return False


def main():
    """Generate speech for three example sentences using the REST API."""

    base_url = "http://127.0.0.1:8000"

    print("=" * 60)
    print("ToucanTTS Microservice Client Example")
    print("=" * 60)
    print()

    # Check if service is running
    print("Checking service health...")
    if not check_health(base_url):
        print("\n✗ Service is not available. Exiting.")
        sys.exit(1)
    print()

    # Define test cases
    test_cases = [
        {
            "text": "My spatula is not a rutabega",
            "output": "spatula_rutabega.wav",
            "description": "Testing unusual object comparisons and multi-syllabic nonsense words"
        },
        {
            "text": "Shoes are rarely edible",
            "output": "shoes_edible.wav",
            "description": "Testing absurdist statements about everyday objects"
        },
        {
            "text": "Hot air baloons are often purple",
            "output": "balloons_purple.wav",
            "description": "Testing misspelling ('baloons') and color descriptors"
        }
    ]

    # Synthesize speech for each test case
    success_count = 0
    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/3] Synthesizing: \"{test['text']}\"")
        print(f"       Purpose: {test['description']}")
        print(f"       API endpoint: POST {base_url}/synthesize")

        success = synthesize_speech(
            text=test["text"],
            output_file=test["output"],
            language="eng",
            speed=1.0,
            base_url=base_url
        )

        if success:
            # Verify file was created
            file_size = Path(test["output"]).stat().st_size
            print(f"       ✓ Saved to {test['output']} ({file_size:,} bytes)")
            success_count += 1
        else:
            print(f"       ✗ Failed to generate {test['output']}")

        print()

    # Summary
    print("=" * 60)
    if success_count == len(test_cases):
        print(f"✓ All {success_count}/{len(test_cases)} audio files generated successfully!")
    else:
        print(f"⚠ Only {success_count}/{len(test_cases)} files generated successfully")
    print("=" * 60)
    print()

    if success_count > 0:
        print("Generated files:")
        for test in test_cases[:success_count]:
            print(f"  - {test['output']}")

        print("\nYou can play these files with:")
        print("  - Command line: aplay spatula_rutabega.wav")
        print("  - GUI: Open in any audio player")
        print("  - Python: Use sounddevice, pygame, or similar libraries")
        print()
        print("API Documentation available at:")
        print(f"  {base_url}/docs (Interactive Swagger UI)")
        print(f"  {base_url}/redoc (ReDoc documentation)")


if __name__ == "__main__":
    main()
