"""
Video Editor Module
Creates videos using MoviePy with audio, images, and text overlays
"""
import random
from pathlib import Path
from moviepy.editor import (
    VideoClip, ImageClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips
)
from moviepy.video.fx.all import fadein, fadeout
import numpy as np
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import VIDEO_RESOLUTION, VIDEO_FPS, OUTPUT_DIR, PEXELS_API_KEY


class VideoEditor:
    """Create and edit videos programmatically"""
    
    def __init__(self):
        self.resolution = VIDEO_RESOLUTION
        self.fps = VIDEO_FPS
        self.output_dir = OUTPUT_DIR
    
    def create_video(self, audio_path, thumbnail_path, script_data, output_path=None):
        """Create a complete video from audio and visuals"""
        print("\n" + "="*50)
        print("VIDEO CREATION PIPELINE")
        print("="*50)
        
        if not output_path:
            output_path = self.output_dir / "final_video.mp4"
        
        # Load audio
        print("📼 Loading audio...")
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration
        
        print(f"Audio duration: {duration:.1f} seconds")
        
        # Create video clips
        print("🎬 Creating video clips...")
        clips = []
        
        # Method 1: Use thumbnail as static background with text overlays
        clips = self._create_clips_with_text_overlays(
            thumbnail_path, script_data, duration
        )
        
        # Concatenate all clips
        print("🔗 Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        print("🎵 Adding audio track...")
        final_video = final_video.set_audio(audio)
        
        # Export video
        print(f"💾 Exporting video to: {output_path}")
        print("This may take several minutes...")
        
        final_video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(self.output_dir / 'temp-audio.m4a'),
            remove_temp=True,
            preset='medium',
            threads=4
        )
        
        # Clean up
        audio.close()
        final_video.close()
        for clip in clips:
            clip.close()
        
        print(f"✅ Video created successfully: {output_path}")
        return output_path
    
    def _create_clips_with_text_overlays(self, thumbnail_path, script_data, duration):
        """Create video clips with text overlays on thumbnail background"""
        clips = []
        
        # Load thumbnail as background
        bg_clip = ImageClip(str(thumbnail_path)).set_duration(duration)
        bg_clip = bg_clip.resize(self.resolution)
        
        # Create segments based on script sections
        sections = self._get_script_sections(script_data)
        
        if not sections:
            # Fallback: just use thumbnail for entire duration
            return [bg_clip]
        
        # Calculate duration per section
        section_duration = duration / len(sections)
        
        current_time = 0
        for i, section in enumerate(sections):
            # Create background for this section
            section_bg = bg_clip.subclip(current_time, min(current_time + section_duration, duration))
            
            # Add text overlay
            if section.get("title"):
                text_clip = self._create_text_overlay(
                    section["title"],
                    section_duration,
                    position='top'
                )
                section_clip = CompositeVideoClip([section_bg, text_clip])
            else:
                section_clip = section_bg
            
            # Add fade transitions
            if i == 0:
                section_clip = fadein(section_clip, 1)
            if i == len(sections) - 1:
                section_clip = fadeout(section_clip, 1)
            
            clips.append(section_clip)
            current_time += section_duration
        
        return clips
    
    def _get_script_sections(self, script_data):
        """Extract sections from script data"""
        sections = []
        
        # Add hook
        if script_data.get("hook"):
            sections.append({"title": "Introduction", "content": script_data["hook"]})
        
        # Add main content sections
        for section in script_data.get("main_content", []):
            sections.append({
                "title": section.get("section_title", ""),
                "content": section.get("content", "")
            })
        
        # Add conclusion
        if script_data.get("conclusion"):
            sections.append({"title": "Conclusion", "content": script_data["conclusion"]})
        
        return sections
    
    def _create_text_overlay(self, text, duration, position='center'):
        """Create a text overlay clip"""
        try:
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=60,
                color='white',
                font='DejaVu-Sans-Bold',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(self.resolution[0] - 200, None)
            )
            
            # Set duration and position
            txt_clip = txt_clip.set_duration(duration)
            
            if position == 'top':
                txt_clip = txt_clip.set_position(('center', 100))
            elif position == 'bottom':
                txt_clip = txt_clip.set_position(('center', self.resolution[1] - 200))
            else:
                txt_clip = txt_clip.set_position('center')
            
            # Add fade in/out
            txt_clip = fadein(txt_clip, 0.5)
            txt_clip = fadeout(txt_clip, 0.5)
            
            return txt_clip
        except Exception as e:
            print(f"⚠️ Could not create text overlay: {e}")
            # Return empty clip
            return VideoClip(lambda t: np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)).set_duration(duration)
    
    def _create_color_background(self, duration, color=(30, 30, 46)):
        """Create a solid color background clip"""
        def make_frame(t):
            return np.full((self.resolution[1], self.resolution[0], 3), color, dtype=np.uint8)
        
        return VideoClip(make_frame, duration=duration)
    
    def _download_stock_footage(self, query, duration):
        """Download stock footage from Pexels (if API key available)"""
        if not PEXELS_API_KEY:
            return None
        
        try:
            import requests
            
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("videos"):
                video_url = data["videos"][0]["video_files"][0]["link"]
                
                # Download video
                video_path = self.output_dir / f"stock_{query.replace(' ', '_')}.mp4"
                video_response = requests.get(video_url)
                
                with open(video_path, 'wb') as f:
                    f.write(video_response.content)
                
                return video_path
        except Exception as e:
            print(f"⚠️ Could not download stock footage: {e}")
        
        return None


def main():
    """Test the video editor"""
    from audio_producer import AudioProducer
    from thumbnail_creator import ThumbnailCreator
    
    print("Testing Video Editor...")
    
    # Create test audio
    print("\n1. Creating test audio...")
    audio_producer = AudioProducer()
    test_text = """
    Welcome to this video about artificial intelligence.
    AI is transforming our world in incredible ways.
    From virtual assistants to self-driving cars,
    AI is everywhere. Thank you for watching!
    """
    audio_path, _ = audio_producer.create_full_audio(test_text)
    
    # Create test thumbnail
    print("\n2. Creating test thumbnail...")
    thumbnail_creator = ThumbnailCreator()
    thumbnail_path = thumbnail_creator.create_thumbnail("AI BASICS", "Complete Guide")
    
    # Create test script data
    script_data = {
        "topic": "AI Basics",
        "hook": "Welcome!",
        "introduction": "Let's learn about AI",
        "main_content": [
            {"section_title": "What is AI?", "content": "AI explained..."},
            {"section_title": "Applications", "content": "AI in real world..."}
        ],
        "conclusion": "Thanks for watching!"
    }
    
    # Create video
    print("\n3. Creating video...")
    editor = VideoEditor()
    video_path = editor.create_video(audio_path, thumbnail_path, script_data)
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50)
    print(f"Video: {video_path}")


if __name__ == "__main__":
    main()
