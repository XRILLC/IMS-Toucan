# Docstring Coverage Status

**Date**: 2025-11-03
**Current Coverage**: 22.2% (242/1089 items)
**Target**: 80%

## Progress

### Before
- Overall: 21.6% (262/1215 items)
- Classes: 38.0%
- Functions: 18.5%

### After Initial Work
- Overall: 22.2% (242/1089 items)
- Classes: 39.9% (61/153)
- Functions: 19.3% (181/936)

## Completed Documentation

### ✅ Priority 1: Public API (InferenceInterfaces/ToucanTTSInterface.py)
**Status**: COMPLETE

Fully documented with comprehensive Google-style docstrings:
- `ToucanTTSInterface` class - Full description with usage examples
- `__init__()` - All 4 parameters documented with types, defaults, examples
- `set_utterance_embedding()` - Voice cloning documentation with examples
- `set_language()` - Language switching for 7000+ languages
- `read_to_file()` - Complete documentation of primary synthesis method
  - All 13 parameters with types, ranges, defaults
  - Multiple examples for common use cases
  - Raises section for error handling
  - Best practices notes

**Impact**: End users can now use the API effectively with IDE autocomplete and help()

## Remaining Work

### Priority Files (Need Documentation)

#### Priority 2: Preprocessing/TextFrontend.py (1,152 LOC)
- **Current**: Minimal docstrings
- **Needed**: Document 7000-language text preprocessing pipeline
- **Estimated**: 200+ LOC of docstrings

Key classes/functions needing docs:
- `ArticulatoryCombinedTextFrontend` class
- `__init__()` - Language configuration
- `string_to_tensor()` - Text to phoneme conversion
- `get_phone_string()` - Phoneme extraction
- Language-specific handlers (50+ language branches)

#### Priority 3: Modules/ToucanTTS/ToucanTTS.py (528 LOC)
- **Current**: Class docstring exists, methods lack detail
- **Needed**: Document model architecture and forward pass
- **Estimated**: 150+ LOC of docstrings

Key components needing docs:
- `ToucanTTS.__init__()` - 40+ architecture parameters
- `forward()` - Inference pipeline
- `inference()` - High-level generation method
- Model subcomponents (encoder, decoder, predictors)

#### Priority 4: Preprocessing/AudioPreprocessor.py
- **Current**: 55.6% coverage
- **Needed**: Finish remaining methods
- **Estimated**: 50 LOC of docstrings

#### Priority 5: run_text_to_file_reader.py
- **Current**: 0% coverage
- **Needed**: Document user-facing script
- **Estimated**: 30 LOC of docstrings

#### Priority 6: Utility/path_to_transcript_dicts.py (2,418 LOC)
- **Current**: 1.8% coverage (5/281 functions)
- **Needed**: Document all dataset builder functions
- **Estimated**: 500+ LOC of docstrings

This file has 281 functions, all dataset loaders returning `{audio_path: transcript}` dicts.
Most can be templatized:

```python
def build_path_to_transcript_DATASET_NAME(root):
    """Build path-to-transcript mapping for DATASET_NAME corpus.

    Args:
        root: Root directory containing the dataset.

    Returns:
        Dict mapping absolute audio file paths to transcript strings.

    Example:
        >>> mapping = build_path_to_transcript_DATASET_NAME("/data/DATASET")
        >>> print(mapping["/data/DATASET/audio/file1.wav"])
        "transcript text"
    """
```

### Lower Priority

- Modules/Aligner/ - Training code (less critical for users)
- Modules/Vocoder/ - HiFiGAN implementation (vendored code)
- Modules/GeneralLayers/ - ESPNet components (vendored code)
- Recipes/ - Training recipes (advanced users)
- Utility/utils.py - Helper functions (421 LOC, mixed usage)

## Tooling Configured

All tools are configured in `pyproject.toml`:

```bash
# Check docstring coverage
interrogate InferenceInterfaces/ Preprocessing/ Modules/

# Generate coverage report
interrogate --fail-under 80 --verbose 2 .

# Format code
ruff format .

# Type check
mypy InferenceInterfaces/ Preprocessing/
```

## Recommendations

### Immediate Next Steps
1. **Document TextFrontend.py** - Critical for understanding multilingual support
2. **Document ToucanTTS.py** - Core model architecture
3. **Templatize dataset builders** - 281 functions can use same pattern

### Long-term Strategy
1. **Enforce in CI** - Add interrogate to GitHub Actions
2. **Pre-commit hooks** - Block commits with undocumented public methods
3. **Documentation site** - Use Sphinx to generate API reference from docstrings
4. **Examples** - Add Jupyter notebooks demonstrating all features

### Template for Remaining Files

Google-style docstring template:

```python
def function_name(param1: type, param2: type) -> return_type:
    """One-line summary.

    Detailed description explaining what the function does and when to use it.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this exception is raised.

    Example:
        >>> result = function_name(value1, value2)
        >>> print(result)
        expected_output
    """
```

## Progress Tracking

- [x] Public API (InferenceInterfaces/) - 100%
- [ ] Text Processing (Preprocessing/TextFrontend.py) - ~10%
- [ ] Core Model (Modules/ToucanTTS/ToucanTTS.py) - ~30%
- [ ] Audio Processing (Preprocessing/AudioPreprocessor.py) - 56%
- [ ] Dataset Builders (Utility/path_to_transcript_dicts.py) - 2%
- [ ] User Scripts (run_*.py) - 0%
- [ ] Training Code (Recipes/, Modules/Aligner/) - ~10%

**Estimated work remaining**: 1,000-1,500 LOC of docstrings to reach 80% coverage

**Priority**: Focus on user-facing code first (Public API ✓, TextFrontend, ToucanTTS)
