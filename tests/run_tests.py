#!/usr/bin/env python3
"""
Test runner for NEPTR AI Assistant
Run all tests or specific test files
"""

import os
import sys
import subprocess

def run_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    print("🤖 NEPTR Test Suite")
    print("=" * 30)
    
    # Available tests
    tests = [
        ("test_neptr.py", "System health check"),
        ("test_espeak_tts.py", "espeak TTS test"),
        ("test_voice.py", "Voice settings test"),
        ("test_wake_words.py", "Wake word detection test"),
        ("test_voice_neptr.py", "Voice assistant simulation")
    ]
    
    print("Available tests:")
    for i, (test_file, description) in enumerate(tests, 1):
        print(f"  {i}. {test_file} - {description}")
    
    print("\nOptions:")
    print("  all - Run all tests")
    print("  <number> - Run specific test")
    print("  q - Quit")
    
    while True:
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == "q":
            print("Goodbye! 🤖🥧")
            break
        elif choice == "all":
            print("\n🚀 Running all tests...")
            all_passed = True
            for test_file, _ in tests:
                if not run_test(test_file):
                    all_passed = False
                print()
            
            if all_passed:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
            break
        elif choice.isdigit():
            test_num = int(choice)
            if 1 <= test_num <= len(tests):
                test_file, _ = tests[test_num - 1]
                run_test(test_file)
                break
            else:
                print("❌ Invalid test number")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
