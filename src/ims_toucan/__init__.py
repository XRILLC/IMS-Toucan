"""IMS-Toucan: Massively Multilingual Text-to-Speech Toolkit.

This package provides a comprehensive TTS system supporting 7000+ languages
with FastSpeech 2 architecture, articulatory features, and HiFiGAN vocoder.

Example:
    >>> from ims_toucan import ToucanTTS
    >>> tts = ToucanTTS(device="cpu", language="eng")
    >>> tts.read_to_file(["Hello world"], "output.wav")
"""

__version__ = "0.1.0"
__author__ = "Florian Lux"
__email__ = "florian.lux@ims.uni-stuttgart.de"

# Public API - will be properly wired up after moving code to src/
__all__ = ["__version__"]
