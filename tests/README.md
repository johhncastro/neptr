# 🧪 NEPTR Test Suite

This folder contains all the test files for the NEPTR AI Assistant.

## 📋 Available Tests

### `test_neptr.py`
**System health check** - Comprehensive test of all components:
- Import verification
- Audio system testing
- Vosk model validation
- Configuration checks
- OpenAI API connectivity

### `test_espeak_tts.py`
**espeak TTS test** - Simple test of the current TTS configuration:
- Tests the configured espeak voice
- Quick verification that TTS is working

### `test_voice.py`
**Voice settings test** - Test different voice options:
- Different speech speeds
- Different voice pitches
- Interactive voice testing

### `test_wake_words.py`
**Wake word detection test** - Test wake word recognition:
- Standard wake phrases
- Common mishears ("hello after" vs "hello neptr")
- Edge cases and false positives

### `test_voice_neptr.py`
**Voice assistant simulation** - Simulate voice interactions:
- API connection testing
- Command processing simulation
- Response verification

### `run_tests.py`
**Test runner** - Easy way to run all tests:
- Interactive menu
- Run all tests or specific ones
- Organized test execution

## 🚀 Running Tests

### Run All Tests
```bash
python3 tests/run_tests.py
```

### Run Specific Tests
```bash
# System health check
python3 tests/test_neptr.py

# TTS test
python3 tests/test_espeak_tts.py

# Voice options test
python3 tests/test_voice.py

# Wake word test
python3 tests/test_wake_words.py

# Voice simulation
python3 tests/test_voice_neptr.py
```

## 🎯 Test Purposes

- **Debugging**: Use tests to identify issues
- **Verification**: Ensure everything works after changes
- **Development**: Test new features before integration
- **Troubleshooting**: Isolate problems in specific components

## 📝 Notes

- All tests are designed to run independently
- Tests will provide clear feedback on what's working/failing
- Some tests require internet connection (OpenAI API)
- Audio tests may play sounds - adjust volume accordingly
