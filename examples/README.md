# IMS-Toucan Usage Examples

This directory contains example scripts demonstrating how to use IMS-Toucan for various text-to-speech tasks.

## Quick Start

### Installation

First, install IMS-Toucan as a Python package:

```bash
# From the project root
uv pip install -e .

# Or using pip
pip install -e .
```

### Basic Library Usage

Run the basic example to generate test audio:

```bash
python examples/library_usage_example.py
```

This generates three WAV files demonstrating the library's ability to handle:
- Unusual word combinations and multi-syllabic words
- French loanword pronunciation
- Archaic vocabulary

**Generated files:**
- `horse_waffles.wav` - "My horse is enamored of eating waffles" (115 KB)
- `souffle_climb.wav` - "A nice souffle is hard to climb with" (115 KB)
- `ruffian_coat.wav` - "A ruffian stole my coat" (85 KB)

All files are 16-bit PCM WAVE audio, mono 24kHz.

## Example 1: Basic Library Import

```python
from ims_toucan import ToucanTTS

# Initialize TTS with English language
tts = ToucanTTS(device="cpu", language="eng")

# Generate speech to file
tts.read_to_file(
    text_list=["Hello world!"],
    file_location="output.wav"
)
```

## Example 2: Multilingual Synthesis

```python
from ims_toucan import ToucanTTS

# Initialize TTS
tts = ToucanTTS(device="cuda", language="eng")

# English
tts.set_language("eng")
tts.read_to_file(["Hello world"], "english.wav")

# German
tts.set_language("deu")
tts.read_to_file(["Guten Tag"], "german.wav")

# Mandarin
tts.set_language("cmn")
tts.read_to_file(["你好世界"], "mandarin.wav")

# French
tts.set_language("fra")
tts.read_to_file(["Bonjour le monde"], "french.wav")
```

## Example 3: Voice Cloning

```python
from ims_toucan import ToucanTTS

tts = ToucanTTS(device="cuda", language="eng")

# Clone voice from reference audio
tts.set_utterance_embedding("reference_voice.wav")

# Generate speech in the cloned voice
tts.read_to_file(
    text_list=["This is my cloned voice speaking"],
    file_location="cloned_output.wav"
)
```

## Example 4: Controllable Prosody

```python
from ims_toucan import ToucanTTS

tts = ToucanTTS(device="cuda", language="eng")

# Slower speech (1.3x slower)
tts.read_to_file(
    text_list=["This is slow speech"],
    file_location="slow.wav",
    duration_scaling_factor=1.3
)

# Faster speech (0.8x speed = 25% faster)
tts.read_to_file(
    text_list=["This is fast speech"],
    file_location="fast.wav",
    duration_scaling_factor=0.8
)
```

## Example 5: Batch Processing

```python
from ims_toucan import ToucanTTS

tts = ToucanTTS(device="cuda", language="eng")

# Multiple sentences in one file
sentences = [
    "First sentence.",
    "Second sentence.",
    "Third sentence."
]

tts.read_to_file(
    text_list=sentences,
    file_location="batch_output.wav"
)
```

## Example 6: Using the CLI

Instead of Python scripts, you can use the command-line interface:

```bash
# Simple synthesis
toucan-tts --text "Hello world" --output hello.wav --language eng

# With voice cloning
toucan-tts --text "Cloned voice" --output cloned.wav \
    --reference voice.wav --language eng

# Faster speech
toucan-tts --text "Fast speech" --output fast.wav \
    --speed 1.25 --language eng

# Batch processing from text file
toucan-infer --input sentences.txt --output-dir outputs/ --language eng
```

## Example 7: Interactive Mode

```bash
# Interactive CLI - type text and press Enter to synthesize
toucan-tts --interactive --language eng
```

## API Reference

### ToucanTTS Class

```python
class ToucanTTS:
    """High-level interface for ToucanTTS text-to-speech synthesis."""

    def __init__(self, device="cpu", tts_model_path=None,
                 vocoder_model_path=None, language="eng"):
        """
        Args:
            device: "cpu" or "cuda"
            tts_model_path: Path to model or None (auto-download)
            vocoder_model_path: Path to vocoder or None (auto-download)
            language: ISO 639-3 code (e.g., "eng", "deu", "cmn")
        """

    def set_language(self, lang_id):
        """Change synthesis language."""

    def set_utterance_embedding(self, reference_audio_path):
        """Clone voice from reference audio."""

    def read_to_file(self, text_list, file_location,
                     duration_scaling_factor=1.0,
                     prosody_creativity=0.0):
        """Generate speech audio to WAV file."""
```

## Supported Languages

IMS-Toucan supports 7000+ languages via ISO 639-3 codes. Common examples:

| Language | Code | Example Text |
|----------|------|--------------|
| English | eng | "Hello world" |
| German | deu | "Guten Tag" |
| French | fra | "Bonjour" |
| Spanish | spa | "Hola mundo" |
| Italian | ita | "Ciao mondo" |
| Portuguese | por | "Olá mundo" |
| Russian | rus | "Привет мир" |
| Mandarin | cmn | "你好世界" |
| Japanese | jpn | "こんにちは世界" |
| Korean | kor | "안녕하세요 세계" |
| Arabic | arb | "مرحبا بالعالم" |
| Hindi | hin | "नमस्ते दुनिया" |

For the complete list, see `Utility/language_list.md`.

## Audio Format

All generated audio files have the following specifications:

- **Format**: WAV (WAVE audio)
- **Bit Depth**: 16-bit PCM
- **Sample Rate**: 24 kHz
- **Channels**: Mono
- **Encoding**: PCM (uncompressed)

## Performance Tips

1. **Use GPU**: Set `device="cuda"` for 10x+ speedup
2. **Batch Processing**: Use `read_to_file()` with multiple sentences for efficiency
3. **CLI for Automation**: Use `toucan-infer` for batch processing large text files
4. **Model Caching**: Models download once and are cached in `Models/` directory

## Troubleshooting

**Import Error:**
```bash
# Make sure package is installed
uv pip install -e .
```

**CUDA Error:**
```python
# Fall back to CPU
tts = ToucanTTS(device="cpu", language="eng")
```

**Model Download Issues:**
```bash
# Check internet connection
# Models auto-download from Hugging Face on first run
# Cached in Models/ directory
```

**Audio Quality Issues:**
```python
# Try adjusting prosody creativity
tts.read_to_file(
    text_list=["Your text"],
    file_location="output.wav",
    prosody_creativity=0.1  # Add slight variation
)
```

## Additional Resources

- **Documentation**: See `CLAUDE.md` for training recipes and advanced usage
- **Public API**: Full documentation in `InferenceInterfaces/ToucanTTSInterface.py`
- **CLI Help**: Run `toucan-tts --help` for all CLI options
- **Web Interface**: See `Utility/simple_demo.py` for Gradio web UI

## Testing

To verify your installation works correctly, run the example:

```bash
python examples/library_usage_example.py
```

This should generate three WAV files without errors. Play them with:

```bash
# Linux
aplay horse_waffles.wav

# macOS
afplay horse_waffles.wav

# Windows (PowerShell)
Start-Process horse_waffles.wav
```

## License

IMS-Toucan is licensed under Apache 2.0. See `LICENSE` for details.

Third-party components (ESPNet, EnCodec, BigVGAN, HiFiGAN) retain their original licenses. See `THIRD_PARTY_LICENSES.md` for attribution.
