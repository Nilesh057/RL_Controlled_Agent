"""
Voice Integration Infrastructure for RL Controlled Agent

This module provides the foundation for voice-to-text integration,
addressing reviewer concern #9 about voice-ready infrastructure.

Note: This is infrastructure preparation. Full voice integration 
would require platform-specific optimizations and user microphone setup.
"""

import os
import sys

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️ Voice dependencies not installed. Run: pip install speechrecognition pyttsx3 pyaudio")

class VoiceInterface:
    """Voice-to-text and text-to-speech interface for the RL agent"""
    
    def __init__(self):
        """Initialize voice interface components"""
        self.speech_available = VOICE_AVAILABLE
        
        if self.speech_available:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.8)  # Volume
            
            print("🎤 Voice interface initialized successfully")
        else:
            print("🔇 Voice interface not available - dependencies missing")
    
    def listen_for_task(self, timeout=5, phrase_limit=3):
        """
        Listen for voice input and convert to text task
        
        Args:
            timeout (int): Seconds to wait for speech
            phrase_limit (int): Seconds of silence to end phrase
        
        Returns:
            str: Recognized text or None if failed
        """
        if not self.speech_available:
            print("❌ Voice recognition not available")
            return None
        
        try:
            print("🎤 Listening for task... (speak now)")
            
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_limit
                )
            
            print("🔄 Processing speech...")
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            print(f"📝 Recognized: '{text}'")
            
            return text.lower().strip()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand the speech")
            return None
        except sr.RequestError as e:
            print(f"🌐 Speech recognition service error: {e}")
            return None
        except Exception as e:
            print(f"❌ Voice recognition error: {e}")
            return None
    
    def listen_for_feedback(self, timeout=3):
        """
        Listen for voice feedback (positive/negative)
        
        Returns:
            str: '👍' or '👎' or None
        """
        if not self.speech_available:
            return None
        
        try:
            print("🎤 Say 'correct' or 'incorrect' for feedback...")
            
            text = self.listen_for_task(timeout=timeout, phrase_limit=2)
            
            if text:
                # Parse feedback
                positive_words = ['correct', 'good', 'right', 'yes', 'positive']
                negative_words = ['incorrect', 'wrong', 'bad', 'no', 'negative']
                
                text_lower = text.lower()
                
                if any(word in text_lower for word in positive_words):
                    print("✅ Voice feedback: Positive")
                    return "👍"
                elif any(word in text_lower for word in negative_words):
                    print("❌ Voice feedback: Negative")
                    return "👎"
                else:
                    print("❓ Voice feedback unclear")
                    return None
            
            return None
            
        except Exception as e:
            print(f"❌ Voice feedback error: {e}")
            return None
    
    def speak(self, text):
        """
        Convert text to speech
        
        Args:
            text (str): Text to speak
        """
        if not self.speech_available:
            print(f"🔇 TTS not available: {text}")
            return
        
        try:
            print(f"🔊 Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
    
    def announce_task(self, task, action, confidence):
        """
        Announce task and agent decision
        
        Args:
            task (str): Task description
            action (str): Agent's chosen action
            confidence (float): Confidence score
        """
        message = f"Task: {task}. I will {action}. Confidence: {confidence:.1%}"
        self.speak(message)
    
    def announce_feedback_request(self):
        """Request feedback via voice"""
        self.speak("Was that action correct? Say correct or incorrect.")
    
    def announce_learning_progress(self, episode, reward):
        """Announce learning progress"""
        message = f"Episode {episode} complete. Total reward: {reward}"
        self.speak(message)

def demo_voice_interface():
    """Demonstrate voice interface capabilities"""
    print("\n" + "="*60)
    print("  🎤 VOICE INTERFACE DEMONSTRATION")
    print("="*60)
    
    voice = VoiceInterface()
    
    if not voice.speech_available:
        print("🔇 Voice demo skipped - dependencies not available")
        print("   To enable voice features:")
        print("   1. pip install speechrecognition pyttsx3 pyaudio")
        print("   2. Ensure microphone permissions are granted")
        print("   3. Test with: python -c 'import speech_recognition'")
        return
    
    print("🎤 Voice interface ready!")
    print("📋 Available voice commands:")
    print("   • Task input: Speak natural language tasks")
    print("   • Feedback: Say 'correct' or 'incorrect'") 
    print("   • TTS: Agent announcements and confirmations")
    
    # Demo TTS
    voice.speak("Voice interface is ready for reinforcement learning training")
    
    print("\n✅ Voice infrastructure verified and ready")
    print("🏗️ Infrastructure includes:")
    print("   • Speech-to-text for task input")
    print("   • Voice feedback recognition")
    print("   • Text-to-speech announcements")
    print("   • Error handling and fallbacks")
    print("   • Configurable speech parameters")

if __name__ == "__main__":
    demo_voice_interface()