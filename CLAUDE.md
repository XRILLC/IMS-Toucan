# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IMS Toucan is a massively multilingual Text-to-Speech (TTS) toolkit supporting 7000+ languages. It's developed at the Institute for Natural Language Processing (IMS), University of Stuttgart. The system uses FastSpeech 2 architecture with articulatory features, ConditionalFlowMatching PostNet, and HiFiGAN vocoder.

## Development Environment

### Prerequisites
- Python 3.13+ (required)
- CUDA-enabled GPU (for training; inference works on CPU)
- System packages: `libsndfile1`, `espeak-ng`, `ffmpeg`, `libasound-dev`, `libportaudio2`, `libsqlite3-dev`
- Additional for Korean: `mecab`, `mecab-ko-dic` (for mecab-python3)

### Setup

#### Modern Installation (Recommended)
```bash
# Install uv (fast dependency resolver)
pip install uv

# Create virtual environment and install core dependencies
uv venv
source .venv/bin/activate
uv sync

# Or install with all optional features
uv sync --extra all

# Available extras:
# --extra asian-extra  # Japanese/Korean support (pykakasi, jamo, g2pk)
# --extra gui          # PyQt5 interfaces
# --extra web          # Gradio web interface
# --extra training     # Weights & Biases logging
# --extra all          # Everything
```

#### Legacy Installation (Backward Compatible)
```bash
python -m venv <venv_path>
source <venv_path>/bin/activate
pip install --no-cache-dir -r requirements.txt
```

### Storage Configuration
Edit `Utility/storage_config.py` to customize:
- `MODEL_DIR`: checkpoint storage (default: `Models/`)
- `PREPROCESSING_DIR`: cached preprocessed data (default: `Corpora/`)

## Common Commands

### Inference
```bash
# Run text-to-file conversion (creates audio files)
python run_text_to_file_reader.py

# Run interactive GUI demo
python run_simple_GUI_demo.py
python run_advanced_GUI_demo.py
```

### Training
```bash
# Single GPU training
python run_training_pipeline.py <pipeline_name> --gpu_id 0

# Multi-GPU training (must use torchrun, not compatible with nohup - use tmux instead)
torchrun --standalone --nproc_per_node=4 --nnodes=1 run_training_pipeline.py <pipeline_name> --gpu_id "0,1,2,3"

# Common training options:
# --resume                    # Auto-load highest checkpoint
# --resume_checkpoint <path>  # Load specific checkpoint
# --finetune                  # Fine-tune from checkpoint
# --model_save_dir <path>     # Custom checkpoint directory
# --wandb                     # Enable Weights & Biases logging
# --wandb_resume_id <id>      # Resume W&B run
```

Available pipelines (see `run_training_pipeline.py`):
- `finetuning_example_simple`: Single-dataset finetuning template
- `finetuning_example_multilingual`: Multi-dataset/multilingual finetuning template
- `nancy`, `eng1`, `eng2`, `deu`, `asian`, `stage1`, `stage2`, `stage3`: Pre-configured training recipes
- `tt_it`: Integration test
- `aligner`, `hifigan`, `e2e`, `be2e`: Advanced component training

### Data Quality Tools
```bash
# Score dataset and identify problematic samples
python run_scorer.py
```

The scorer finds and optionally removes samples with high loss values (outliers).

## Architecture

### Core Components

**InferenceInterfaces/**
- `ToucanTTSInterface.py`: Main inference API with `read_to_file()` and `read_aloud()` methods
- `ControllableInterface.py`: Controllable speaker embedding generation
- `UtteranceCloner.py`: Prosody cloning capabilities

**Modules/**
- `ToucanTTS/`: FastSpeech 2 variant with duration/pitch/energy predictors, ConditionalFlowMatching PostNet
  - `ToucanTTS.py`: Main model definition
  - `toucantts_train_loop.py`: Training loop implementation
  - `TTSDataset.py`: Dataset handling
- `Aligner/`: Forced alignment between text and audio
- `Vocoder/`: HiFiGAN and BigVGAN neural vocoders
- `EmbeddingModel/`: Speaker embedding (GST, StyleTTS encoder)
- `GeneralLayers/`: Reusable components (Conformer, attention, convolution)
- `ControllabilityGAN/`: Controllable speaker embedding generation

**Preprocessing/**
- `TextFrontend.py`: Text-to-phoneme conversion supporting 7000+ languages
  - Uses espeak-ng and transphone for G2P
  - Handles language-specific text normalization
  - Converts phonemes to articulatory features
- `AudioPreprocessor.py`: Audio normalization and feature extraction
- `EnCodecAudioPreprocessor.py`: Neural codec-based audio preprocessing
- `Codec/`: EnCodec neural audio codec for space-efficient caching
- `multilinguality/`: Language embedding generation and distance metrics
- `articulatory_features.py`: Phoneme-to-articulatory feature mapping

**Recipes/**
Training pipeline definitions (copied and modified for new datasets).

**Utility/**
- `path_to_transcript_dicts.py`: Dataset loaders returning `{audio_path: transcript}` dicts
- `corpus_preparation.py`: `prepare_tts_corpus()` function for dataset preprocessing
- `WarmupScheduler.py`: Learning rate scheduling
- `Scorer.py`: Dataset quality analysis

### Data Flow

1. **Text → Phonemes**: `TextFrontend.py` converts text to IPA phonemes using language-specific rules
2. **Phonemes → Articulatory Features**: Phonemes mapped to articulatory feature vectors
3. **Features → Acoustic**: `ToucanTTS` predicts duration, pitch, energy, and mel-spectrogram
4. **Acoustic → Audio**: `HiFiGAN` vocoder converts mel-spectrogram to waveform

Training uses neural codec intermediate representation (EnCodec) to save disk space.

## Creating a Training Recipe

### Step 1: Define Dataset in `Utility/path_to_transcript_dicts.py`

Create a function returning `dict[str, str]` mapping absolute audio paths to transcripts:

```python
def build_path_to_transcript_my_dataset(root):
    path_to_transcript = {}
    # ... populate dictionary ...
    return path_to_transcript
```

### Step 2: Create Recipe in `Recipes/`

Copy `finetuning_example_simple.py` (single dataset) or `finetuning_example_multilingual.py` (multiple datasets).

Key modifications:
- Call `prepare_tts_corpus()` with your transcript dict function
- Set `corpus_dir` to a unique cache directory name
- Set `lang` to ISO 639-3 language code (e.g., "eng", "deu", "cmn")
- Adjust `save_dir` for checkpoints
- Tune hyperparameters:
  - `batch_size`: Reduce if OOM errors occur
  - `lr`: 1e-5 for finetuning; up to 1e-4 for large datasets (>1000 samples)
  - `steps`: Depends on data size; fewer steps for small datasets to prevent collapse

**Important**: If adding a new language, you may need to extend `Preprocessing/TextFrontend.py` with language-specific handling.

### Step 3: Register in `run_training_pipeline.py`

```python
from Recipes.my_recipe import run as my_recipe

pipeline_dict = {
    # ...
    "my_shorthand": my_recipe,
}
```

### Step 4: Train

```bash
python run_training_pipeline.py my_shorthand --gpu_id 0 --finetune
```

## Language Support

The toolkit uses ISO 639-3 language codes. For supported languages, see `Utility/language_list.md`. The `TextFrontend` handles language-specific grapheme-to-phoneme conversion, including:
- Mandarin: pypinyin → IPA
- Japanese: Katakana/Hiragana handling
- English: Abbreviation expansion
- Tonal languages: Tone mark processing

Set language during inference:
```python
tts = ToucanTTSInterface(device="cuda", language="eng")
tts.set_language("deu")  # Change language dynamically
```

## Inference API

```python
from InferenceInterfaces.ToucanTTSInterface import ToucanTTSInterface

tts = ToucanTTSInterface(device="cuda", tts_model_path=None)  # None = download default
tts.set_language("eng")  # ISO 639-3 code
tts.set_utterance_embedding("path/to/reference.wav")  # Optional: clone speaker

# Generate audio file
tts.read_to_file(
    text_list=["Hello world.", "This is a test."],
    file_location="output.wav",
    duration_scaling_factor=1.0,  # Speed control
    prosody_creativity=0.0  # Prosody variation
)

# Play through speakers
tts.read_aloud("Hello world.", view=True)  # view=True shows visualization
```

Model paths:
- `None`: Auto-download pretrained model from Hugging Face
- `"path/to/checkpoint.pt"`: Explicit checkpoint path
- `"shorthand"`: Auto-resolve to `Models/ToucanTTS_shorthand/best.pt`

## Training Notes

### GPU Management
- Script sets `CUDA_VISIBLE_DEVICES` internally
- Error messages show GPU0 regardless of specified ID (this is expected behavior)

### Checkpoints
- Saved every epoch to `save_dir`
- Only 5 most recent kept to save space
- `best.pt` created alongside regular checkpoints (optimized for inference)

### Common Issues
- **OOM errors**: Reduce `batch_size` in recipe
- **Loss → NaN**: Data quality issue (use scorer) or learning rate too high
- **Pauses without punctuation**: ASR-transcribed data often problematic; add punctuation

### Data Quality
Clean data is critical. Common problems:
- Mismatched audio/text (wrong transcript)
- Pauses in audio not reflected in text
- Background noise
- Non-speech sounds without text markers

Use `run_scorer.py` to identify and remove problematic samples before training.

## Model Files

Pretrained models auto-download from Hugging Face (Flux9665/ToucanTTS) to `MODEL_DIR`. Models include:
- `ToucanTTS.pt`: Multilingual acoustic model (7000+ languages)
- `Vocoder.pt`: HiFiGAN vocoder
- Language-specific checkpoints available on GitHub releases

## Testing

Integration test pipeline: `python run_training_pipeline.py tt_it --gpu_id 0`

This trains a minimal model to verify the environment is correctly configured.