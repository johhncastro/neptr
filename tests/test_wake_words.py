#!/usr/bin/env python3
"""
Test script for improved wake word detection
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TRIGGERS

def test_wake_word_detection(phrase):
    """Test if a phrase would trigger Neptr"""
    # More flexible wake word detection (same logic as in neptr.py)
    wake_detected = False
    
    # First check for exact matches
    for trigger in TRIGGERS:
        if trigger in phrase.lower():
            wake_detected = True
            break
    
    # Then check for specific misheard patterns
    if not wake_detected:
        # Check for "hello" + any neptr-like word
        if "hello" in phrase.lower():
            neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
            for variation in neptr_variations:
                if variation in phrase.lower():
                    wake_detected = True
                    break
        
        # Check for "hey" + any neptr-like word
        elif "hey" in phrase.lower():
            neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
            for variation in neptr_variations:
                if variation in phrase.lower():
                    wake_detected = True
                    break
        
        # Check for "hi" + any neptr-like word
        elif "hi" in phrase.lower():
            neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
            for variation in neptr_variations:
                if variation in phrase.lower():
                    wake_detected = True
                    break
    
    return wake_detected

def main():
    print("🤖 Testing Improved Wake Word Detection")
    print("=" * 50)
    
    # Test phrases that should trigger Neptr
    test_phrases = [
        # Standard phrases
        "hello neptr",
        "hey neptr", 
        "hi neptr",
        
        # Common mishears
        "hello after",
        "hello nefter",
        "hello nefther",
        "hello nepther",
        "hello neptar",
        "hello neptor",
        "hello neptur",
        
        # Partial matches
        "neptr",
        "nepter",
        "nectar",
        "after",
        "nefter",
        
        # Robot variations
        "hello robot",
        "hey robot",
        "robot",
        "assistant",
        
        # Should NOT trigger
        "hello world",
        "goodbye",
        "computer",
        "random words"
    ]
    
    print("Testing wake word detection:")
    print()
    
    for phrase in test_phrases:
        detected = test_wake_word_detection(phrase)
        status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
        print(f"  \"{phrase}\" -> {status}")
    
    print()
    print("🎯 Key Improvements:")
    print("  • Added many common mishears like 'hello after'")
    print("  • More flexible partial matching")
    print("  • Better handling of speech recognition errors")
    print("  • Should now catch 'hello after' when you say 'hello neptr'")

if __name__ == "__main__":
    main()
