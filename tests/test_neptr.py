#!/usr/bin/env python3
"""
Test script for NEPTR AI Assistant
Run this to verify all components are working correctly
"""

import os
import sys
import subprocess
import importlib.util

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'numpy',
        'sounddevice', 
        'vosk',
        'json',
        'queue',
        'subprocess',
        'time',
        're',
        'random',
        'datetime'
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All imports successful!")
        return True

def test_audio_system():
    """Test audio system components"""
    print("\n🔊 Testing audio system...")
    
    # Test espeak-ng
    if subprocess.run(['which', 'espeak-ng'], capture_output=True).returncode == 0:
        print("  ✅ espeak-ng found")
        
        # Test TTS
        try:
            result = subprocess.run(['espeak-ng', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ espeak-ng working")
            else:
                print("  ❌ espeak-ng not working")
                return False
        except Exception as e:
            print(f"  ❌ espeak-ng error: {e}")
            return False
    else:
        print("  ⚠️  espeak-ng not found, will use fallback")
    
    # Test sounddevice
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"  ✅ sounddevice working ({len(devices)} devices found)")
        
        # List audio devices
        print("  📋 Available audio devices:")
        for i, device in enumerate(devices):
            input_type = 'input' if device.get('max_inputs', 0) > 0 else 'output'
            print(f"    {i}: {device['name']} ({input_type})")
            
    except Exception as e:
        print(f"  ❌ sounddevice error: {e}")
        return False
    
    return True

def test_vosk_model():
    """Test Vosk speech recognition model"""
    print("\n🎤 Testing speech recognition...")
    
    model_path = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")
    
    if not os.path.exists(model_path):
        print(f"  ❌ Vosk model not found at {model_path}")
        print("  📥 Download from: https://alphacephei.com/vosk/models")
        return False
    
    try:
        from vosk import Model
        model = Model(model_path)
        print("  ✅ Vosk model loaded successfully")
        return True
    except Exception as e:
        print(f"  ❌ Vosk model error: {e}")
        return False

def test_config():
    """Test configuration file"""
    print("\n⚙️  Testing configuration...")
    
    try:
        import config
        print("  ✅ config.py loaded successfully")
        
        # Test some key config values
        required_configs = [
            'SAMPLE_RATE', 'BLOCK_SIZE', 'TRIGGERS', 
            'NEPTR_GREETINGS', 'AUDIO_FEEDBACK'
        ]
        
        for config_name in required_configs:
            if hasattr(config, config_name):
                value = getattr(config, config_name)
                print(f"  ✅ {config_name} = {value}")
            else:
                print(f"  ❌ {config_name} not found")
                return False
                
        return True
    except ImportError:
        print("  ⚠️  config.py not found, will use defaults")
        return True
    except Exception as e:
        print(f"  ❌ config.py error: {e}")
        return False

def test_openai_integration():
    """Test OpenAI integration if API key is available"""
    print("\n🤖 Testing OpenAI integration...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ⚠️  OPENAI_API_KEY not set (optional)")
        return True
    
    try:
        import requests
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            print("  ✅ OpenAI API working")
            return True
        else:
            print(f"  ❌ OpenAI API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ OpenAI integration error: {e}")
        return False

def test_main_script():
    """Test if the main script can be imported"""
    print("\n📜 Testing main script...")
    
    try:
        # Test importing the main script
        spec = importlib.util.spec_from_file_location("neptr", "neptr.py")
        neptr_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(neptr_module)
        
        # Test key functions exist
        required_functions = ['tts', 'handle_intent', 'listen_for_command', 'main']
        
        for func in required_functions:
            if hasattr(neptr_module, func):
                print(f"  ✅ {func} function found")
            else:
                print(f"  ❌ {func} function not found")
                return False
        
        print("  ✅ Main script structure looks good")
        return True
        
    except Exception as e:
        print(f"  ❌ Main script error: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 NEPTR AI Assistant - System Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_audio_system,
        test_vosk_model,
        test_config,
        test_openai_integration,
        test_main_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! NEPTR is ready to use!")
        print("\n🚀 To start NEPTR, run:")
        print("   python3 neptr.py")
        print("   or")
        print("   ./start_neptr.sh")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   - Run setup.sh to install dependencies")
        print("   - Download the Vosk model")
        print("   - Check audio permissions")
        print("   - Set OPENAI_API_KEY if using AI features")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
