# Third-Party Code and Licenses

This project includes code from multiple sources under compatible licenses (Apache 2.0 and MIT).

## Vendored Code (Modified/Justified)

### 1. EnCodec (16kHz variant) - `Preprocessing/Codec/`
- **Source**: https://github.com/yangdongchao/AcademiCodec
- **Original**: Meta's EnCodec (https://github.com/facebookresearch/encodec)
- **License**: MIT License
- **Justification**: Modified version supporting 16kHz sampling rate, which the original EnCodec (24kHz only) does not provide. Required for TTS preprocessing pipeline.
- **Files**: `seanet.py` (543 LOC), `vq.py` (615 LOC), `encodec.py` (57 LOC)

### 2. ESPNet Components - `Modules/GeneralLayers/`
- **Source**: https://github.com/espnet/espnet
- **License**: Apache 2.0
- **Files**:
  - `Attention.py` - Multi-head attention mechanisms
  - `Conformer.py` - Conformer encoder (heavily modified)
  - `Convolution.py` - Convolution modules
  - `DurationPredictor.py` - Duration prediction
  - `EncoderLayer.py` - Transformer encoder layers
  - `LengthRegulator.py` - Length regulation for TTS
  - `MultiLayeredConv1d.py` - 1D convolution layers
  - `PositionalEncoding.py` - Positional encodings
  - `PositionwiseFeedForward.py` - FFN layers
  - `STFT.py` - Short-time Fourier transform
  - `LayerNorm.py`, `MultiSequential.py`, `Swish.py`, `VariancePredictor.py`
- **Justification**: Heavily modified from original ESPNet implementations for ToucanTTS architecture. Direct dependency on ESPNet would pull in unnecessary components and version conflicts.
- **Total**: ~1,779 LOC

### 3. StableTTS Components - Flow Matching
- **Source**: https://github.com/KdaiP/StableTTS
- **License**: MIT License
- **Files**:
  - `Modules/ToucanTTS/flow_matching.py` - Conditional Flow Matching decoder
  - `Modules/ToucanTTS/dit.py` - DiT transformer for flow matching
- **Secondary sources referenced**:
  - Matcha-TTS: https://github.com/shivammehta25/Matcha-TTS
  - VITS: https://github.com/jaywalnut310/vits
  - GPT-Fast: https://github.com/pytorch-labs/gpt-fast
- **Justification**: Core architecture component for ToucanTTS decoder. Consolidated from multiple sources.
- **Total**: ~430 LOC

### 4. BigVGAN Vocoder
- **Source**: https://github.com/NVIDIA/BigVGAN (via HiFi-GAN)
- **License**: MIT License
- **Files**: `Modules/Vocoder/BigVGAN.py`, `Modules/Vocoder/AMP.py`, `Modules/Vocoder/Avocodo_Discriminators.py`
- **Justification**: Neural vocoder implementation with anti-aliasing modifications specific to ToucanTTS.
- **Total**: ~830 LOC

### 5. HiFi-GAN Components
- **Source**: https://github.com/jik876/hifi-gan
- **License**: MIT License
- **Files**: `Modules/Vocoder/HiFiGAN_*.py`
- **Justification**: Baseline vocoder architecture, modified for ToucanTTS integration.

### 6. Utility Functions from ESPNet
- **Source**: https://github.com/espnet/espnet
- **License**: Apache 2.0
- **Files**: `Utility/utils.py` (partially)
- **Functions**: `make_pad_mask`, `make_non_pad_mask`, initialization helpers

### 7. AdaSpeech Conditional Layer Normalization
- **Source**: https://github.com/tuanh123789/AdaSpeech
- **License**: Not specified (assumed research code)
- **Files**: `Modules/GeneralLayers/ConditionalLayerNorm.py`
- **Justification**: Speaker adaptation mechanism

## License Compatibility

This project is licensed under **Apache License 2.0**, which is compatible with:
- ✅ MIT License (permissive, can be incorporated)
- ✅ Apache 2.0 (same license)

All vendored code maintains original copyright headers and attributions.

## Dependencies vs. Vendoring

We vendor code when:
1. **Modified implementations** - Significant changes from upstream (e.g., Conformer architecture)
2. **Version requirements** - Specific versions not available via PyPI
3. **Sampling rate modifications** - 16kHz EnCodec vs. 24kHz original
4. **Integration needs** - Code tightly coupled to ToucanTTS architecture

We use PyPI dependencies for:
- Standard ML frameworks (torch, speechbrain)
- Audio processing (librosa, soundfile)
- Phonetics tools (phonemizer, epitran)
- Utilities (numpy, scipy, matplotlib)

## Attribution Requirements

When using IMS-Toucan, please cite:
1. IMS-Toucan (this repository)
2. Meta's EnCodec (for audio compression)
3. ESPNet (for Conformer and attention mechanisms)
4. Original papers for BigVGAN, HiFi-GAN, FastSpeech 2

See README.md for full citations.
