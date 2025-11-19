"""
Audio Producer Module
Generates TTS audio and mixes with background music
"""
import os
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import (
    TTS_LANGUAGE, BACKGROUND_MUSIC_VOLUME, OUTPUT_DIR, ASSETS_DIR,
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
)


class AudioProducer:
    """Generate and mix audio for videos"""
    
    def __init__(self):
        self.music_dir = ASSETS_DIR / "music"
        self.output_dir = OUTPUT_DIR
        self.use_elevenlabs = bool(ELEVENLABS_API_KEY)
    
    def text_to_speech(self, text, output_path=None, use_premium=False):
        """Convert text to speech"""
        if not output_path:
            output_path = self.output_dir / "voiceover.mp3"
        
        print(f"🎙️ Generating TTS audio...")
        print(f"Text length: {len(text)} characters")
        
        # Try ElevenLabs if available and requested
        if use_premium and self.use_elevenlabs:
            try:
                audio_path = self._elevenlabs_tts(text, output_path)
                print(f"✅ Premium TTS generated: {audio_path}")
                return audio_path
            except Exception as e:
                print(f"⚠️ ElevenLabs failed, falling back to gTTS: {e}")
        
        # Use Google TTS (free)
        try:
            tts = gTTS(text=text, lang=TTS_LANGUAGE, slow=False)
            tts.save(str(output_path))
            print(f"✅ TTS audio saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            raise
    
    def _elevenlabs_tts(self, text, output_path):
        """Generate TTS using ElevenLabs API (premium quality)"""
        try:
            import requests
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
        except Exception as e:
            raise Exception(f"ElevenLabs TTS failed: {e}")
    
    def add_background_music(self, voiceover_path, music_path=None, output_path=None):
        """Mix voiceover with background music"""
        print(f"🎵 Adding background music...")
        
        if not output_path:
            output_path = self.output_dir / "audio_final.mp3"
        
        # Load voiceover
        voiceover = AudioSegment.from_mp3(voiceover_path)
        voiceover_duration = len(voiceover)
        
        # Get or create background music
        if music_path and Path(music_path).exists():
            music = AudioSegment.from_file(music_path)
        else:
            # Generate simple background music if none provided
            print("⚠️ No background music found, generating simple ambient track...")
            music = self._generate_ambient_music(voiceover_duration)
        
        # Adjust music volume
        music = music - (20 - int(BACKGROUND_MUSIC_VOLUME * 100))  # Reduce volume
        
        # Loop or trim music to match voiceover duration
        if len(music) < voiceover_duration:
            # Loop music
            loops_needed = (voiceover_duration // len(music)) + 1
            music = music * loops_needed
        
        music = music[:voiceover_duration]
        
        # Fade in/out music
        music = music.fade_in(2000).fade_out(3000)
        
        # Mix audio
        final_audio = voiceover.overlay(music)
        
        # Export
        final_audio.export(output_path, format="mp3", bitrate="192k")
        print(f"✅ Final audio saved to: {output_path}")
        
        return output_path
    
    def _generate_ambient_music(self, duration_ms):
        """Generate simple ambient background music"""
        # Create a simple ambient track with multiple sine waves
        frequencies = [220, 330, 440, 550]  # A3, E4, A4, C#5 (A major chord)
        
        # Generate base tone
        ambient = Sine(frequencies[0]).to_audio_segment(duration=duration_ms, volume=-20)
        
        # Add harmonics
        for freq in frequencies[1:]:
            tone = Sine(freq).to_audio_segment(duration=duration_ms, volume=-25)
            ambient = ambient.overlay(tone)
        
        # Add fade in/out
        ambient = ambient.fade_in(3000).fade_out(3000)
        
        return ambient
    
    def get_audio_duration(self, audio_path):
        """Get duration of audio file in seconds"""
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    
    def create_full_audio(self, text, music_path=None, output_path=None):
        """Complete audio production pipeline"""
        print("\n" + "="*50)
        print("AUDIO PRODUCTION PIPELINE")
        print("="*50)
        
        # Step 1: Generate TTS
        voiceover_path = self.output_dir / "temp_voiceover.mp3"
        self.text_to_speech(text, voiceover_path)
        
        # Step 2: Add background music
        if not output_path:
            output_path = self.output_dir / "audio_final.mp3"
        
        final_audio = self.add_background_music(voiceover_path, music_path, output_path)
        
        # Get duration
        duration = self.get_audio_duration(final_audio)
        print(f"\n✅ Audio production complete!")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Output: {final_audio}")
        
        # Clean up temp file
        if voiceover_path.exists() and voiceover_path != output_path:
            voiceover_path.unlink()
        
        return final_audio, duration


def main():
    """Test the audio producer"""
    producer = AudioProducer()
    
    # Test text
    test_text = """
    Welcome to this comprehensive guide on artificial intelligence.
    In this video, we'll explore the fundamentals of AI and how it's changing our world.
    
    Artificial Intelligence, or AI, refers to computer systems that can perform tasks
    that typically require human intelligence. These tasks include learning, reasoning,
    problem-solving, and understanding natural language.
    
    There are three main types of AI: Narrow AI, which is designed for specific tasks,
    General AI, which can perform any intellectual task a human can do, and
    Super AI, which surpasses human intelligence.
    
    Today, AI is used in many applications, from virtual assistants like Siri and Alexa,
    to recommendation systems on Netflix and Amazon, to self-driving cars and medical diagnosis.
    
    Thank you for watching! Don't forget to like and subscribe for more tech content.
    """
    
    # Create audio
    audio_path, duration = producer.create_full_audio(test_text)
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50)
    print(f"Audio file: {audio_path}")
    print(f"Duration: {duration:.1f}s")


if __name__ == "__main__":
    main()
