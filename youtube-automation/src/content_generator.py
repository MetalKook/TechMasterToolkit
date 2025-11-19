"""
Content Generator Module
Generates evergreen tech video scripts using OpenAI API
"""
import json
import random
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import OPENAI_API_KEY, OPENAI_MODEL, EVERGREEN_TOPICS, OUTPUT_DIR


class ContentGenerator:
    """Generate video scripts using AI"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def generate_topic(self):
        """Generate or select an evergreen tech topic"""
        # Option 1: Random from predefined list
        if random.random() < 0.5:
            return random.choice(EVERGREEN_TOPICS)
        
        # Option 2: Generate new topic using AI
        prompt = """Generate a single evergreen technology topic that would make a great educational YouTube video.
        The topic should be:
        - Timeless and relevant for years
        - Educational and informative
        - Interesting to tech enthusiasts
        - Suitable for a 5-10 minute video
        
        Return ONLY the topic title, nothing else."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_script(self, topic=None):
        """Generate a complete video script"""
        if not topic:
            topic = self.generate_topic()
        
        print(f"📝 Generating script for topic: {topic}")
        
        prompt = f"""Create a comprehensive, engaging YouTube video script about: {topic}

The script should be:
- 5-8 minutes long when spoken (approximately 750-1200 words)
- Educational and easy to understand
- Structured with clear sections
- Engaging and conversational tone
- Include interesting facts and examples
- Evergreen content that stays relevant

Structure the script as JSON with the following format:
{{
    "topic": "topic title",
    "hook": "attention-grabbing opening (15-20 seconds)",
    "introduction": "introduce the topic and what viewers will learn",
    "main_content": [
        {{
            "section_title": "section name",
            "content": "detailed explanation"
        }}
    ],
    "conclusion": "summary and call-to-action",
    "estimated_duration": "duration in minutes"
}}

Make it informative, engaging, and valuable for viewers."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2500
        )
        
        script_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if script_text.startswith("```"):
                script_text = script_text.split("```")[1]
                if script_text.startswith("json"):
                    script_text = script_text[4:]
            
            script_data = json.loads(script_text)
        except json.JSONDecodeError:
            # Fallback: create structured data from text
            script_data = {
                "topic": topic,
                "hook": "Welcome to today's video!",
                "introduction": script_text[:200],
                "main_content": [{"section_title": "Main Content", "content": script_text}],
                "conclusion": "Thanks for watching!",
                "estimated_duration": "5-8 minutes"
            }
        
        # Add metadata
        script_data["generated_at"] = datetime.now().isoformat()
        script_data["model"] = self.model
        
        return script_data
    
    def format_script_for_tts(self, script_data):
        """Convert script data to plain text for TTS"""
        parts = [
            script_data.get("hook", ""),
            script_data.get("introduction", ""),
        ]
        
        # Add main content sections
        for section in script_data.get("main_content", []):
            parts.append(section.get("content", ""))
        
        parts.append(script_data.get("conclusion", ""))
        
        # Join with pauses
        full_text = "\n\n".join(parts)
        return full_text
    
    def save_script(self, script_data, filename=None):
        """Save script to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"script_{timestamp}.json"
        
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Script saved to: {filepath}")
        return filepath


def main():
    """Test the content generator"""
    generator = ContentGenerator()
    
    # Generate a script
    script = generator.generate_script()
    
    # Save it
    filepath = generator.save_script(script)
    
    # Display summary
    print("\n" + "="*50)
    print("SCRIPT SUMMARY")
    print("="*50)
    print(f"Topic: {script['topic']}")
    print(f"Duration: {script.get('estimated_duration', 'N/A')}")
    print(f"Sections: {len(script.get('main_content', []))}")
    print(f"Saved to: {filepath}")
    
    # Show TTS text preview
    tts_text = generator.format_script_for_tts(script)
    print(f"\nTTS Text Length: {len(tts_text)} characters")
    print(f"Preview: {tts_text[:200]}...")


if __name__ == "__main__":
    main()
