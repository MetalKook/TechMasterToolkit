"""
SEO Optimizer Module
Generates SEO-optimized metadata for YouTube videos
"""
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OUTPUT_DIR


class SEOOptimizer:
    """Generate SEO-optimized metadata for YouTube videos"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def generate_metadata(self, script_data):
        """Generate complete SEO metadata from script"""
        topic = script_data.get("topic", "Technology")
        
        print(f"🔍 Generating SEO metadata for: {topic}")
        
        # Get script content for context
        script_summary = self._get_script_summary(script_data)
        
        prompt = f"""Create SEO-optimized YouTube metadata for a video about: {topic}

Video content summary:
{script_summary}

Generate the following in JSON format:
{{
    "title": "Catchy, SEO-optimized title (max 60 characters, include keywords)",
    "description": "Detailed description (300-500 words) with keywords, timestamps, and call-to-action",
    "tags": ["tag1", "tag2", ...] (15-20 relevant tags, mix of broad and specific),
    "hashtags": ["#hashtag1", "#hashtag2", ...] (5-10 trending hashtags for tech niche),
    "keywords": ["keyword1", "keyword2", ...] (primary keywords for SEO)
}}

Requirements:
- Title: Compelling, includes main keyword, under 60 chars
- Description: Detailed, includes keywords naturally, has timestamps, CTA
- Tags: Mix of broad (e.g., "technology") and specific (e.g., "machine learning tutorial")
- Hashtags: Trending, relevant, not too generic
- Keywords: Primary search terms people would use

Make it optimized for YouTube search and discovery!"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        
        metadata_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if metadata_text.startswith("```"):
                metadata_text = metadata_text.split("```")[1]
                if metadata_text.startswith("json"):
                    metadata_text = metadata_text[4:]
            
            metadata = json.loads(metadata_text)
        except json.JSONDecodeError:
            # Fallback metadata
            metadata = {
                "title": topic[:60],
                "description": f"Learn about {topic} in this comprehensive guide.",
                "tags": ["technology", "tech", "tutorial", "education"],
                "hashtags": ["#tech", "#technology", "#tutorial"],
                "keywords": [topic]
            }
        
        # Validate and clean metadata
        metadata = self._validate_metadata(metadata)
        
        # Add generation info
        metadata["generated_at"] = datetime.now().isoformat()
        metadata["original_topic"] = topic
        
        return metadata
    
    def _get_script_summary(self, script_data):
        """Extract key points from script for context"""
        summary_parts = []
        
        if "introduction" in script_data:
            summary_parts.append(script_data["introduction"][:200])
        
        if "main_content" in script_data:
            for section in script_data["main_content"][:3]:  # First 3 sections
                title = section.get("section_title", "")
                summary_parts.append(f"- {title}")
        
        return "\n".join(summary_parts)
    
    def _validate_metadata(self, metadata):
        """Validate and clean metadata"""
        # Ensure title is under 60 characters
        if len(metadata.get("title", "")) > 60:
            metadata["title"] = metadata["title"][:57] + "..."
        
        # Ensure description is not too long (5000 char limit)
        if len(metadata.get("description", "")) > 5000:
            metadata["description"] = metadata["description"][:4997] + "..."
        
        # Limit tags (YouTube allows 500 chars total)
        if "tags" in metadata:
            tags = metadata["tags"][:30]  # Max 30 tags
            metadata["tags"] = tags
        
        # Ensure hashtags start with #
        if "hashtags" in metadata:
            hashtags = []
            for tag in metadata["hashtags"][:15]:  # Max 15 hashtags
                if not tag.startswith("#"):
                    tag = "#" + tag
                hashtags.append(tag)
            metadata["hashtags"] = hashtags
        
        return metadata
    
    def generate_thumbnail_text(self, metadata):
        """Generate text for thumbnail"""
        title = metadata.get("title", "")
        
        # Extract key words (usually first 2-3 words or most important phrase)
        words = title.split()
        
        if len(words) <= 3:
            return title
        
        # Use AI to extract key phrase
        prompt = f"""From this YouTube video title, extract the 2-4 most important words that would work well as large text on a thumbnail:

Title: {title}

Return ONLY the key words, nothing else. Make it punchy and attention-grabbing."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=20
            )
            
            thumbnail_text = response.choices[0].message.content.strip()
            # Remove quotes if present
            thumbnail_text = thumbnail_text.strip('"\'')
            return thumbnail_text
        except:
            # Fallback: use first 3 words
            return " ".join(words[:3])
    
    def save_metadata(self, metadata, filename=None):
        """Save metadata to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metadata_{timestamp}.json"
        
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata saved to: {filepath}")
        return filepath


def main():
    """Test the SEO optimizer"""
    # Load a sample script
    script_data = {
        "topic": "Understanding Artificial Intelligence Basics",
        "introduction": "Artificial Intelligence is transforming our world...",
        "main_content": [
            {"section_title": "What is AI?", "content": "AI is..."},
            {"section_title": "Types of AI", "content": "There are..."},
            {"section_title": "Real-world Applications", "content": "AI is used in..."}
        ]
    }
    
    optimizer = SEOOptimizer()
    
    # Generate metadata
    metadata = optimizer.generate_metadata(script_data)
    
    # Generate thumbnail text
    thumbnail_text = optimizer.generate_thumbnail_text(metadata)
    metadata["thumbnail_text"] = thumbnail_text
    
    # Save it
    filepath = optimizer.save_metadata(metadata)
    
    # Display summary
    print("\n" + "="*50)
    print("SEO METADATA SUMMARY")
    print("="*50)
    print(f"Title: {metadata['title']}")
    print(f"Title Length: {len(metadata['title'])} chars")
    print(f"\nDescription Preview: {metadata['description'][:150]}...")
    print(f"Description Length: {len(metadata['description'])} chars")
    print(f"\nTags ({len(metadata.get('tags', []))}): {', '.join(metadata.get('tags', [])[:5])}...")
    print(f"\nHashtags: {' '.join(metadata.get('hashtags', []))}")
    print(f"\nThumbnail Text: {thumbnail_text}")
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    main()
