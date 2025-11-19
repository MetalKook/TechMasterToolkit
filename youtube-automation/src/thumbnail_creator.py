"""
Thumbnail Creator Module
Creates eye-catching YouTube thumbnails using Pillow
"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import THUMBNAIL_SIZE, OUTPUT_DIR, ASSETS_DIR


class ThumbnailCreator:
    """Create professional YouTube thumbnails"""
    
    def __init__(self):
        self.size = THUMBNAIL_SIZE
        self.fonts_dir = ASSETS_DIR / "fonts"
        self.templates_dir = ASSETS_DIR / "templates"
        
        # Color schemes for tech content
        self.color_schemes = [
            {
                "background": [(30, 30, 46), (24, 24, 37)],  # Dark blue gradient
                "accent": (137, 180, 250),  # Light blue
                "text": (255, 255, 255),
                "shadow": (0, 0, 0)
            },
            {
                "background": [(17, 24, 39), (31, 41, 55)],  # Dark gray gradient
                "accent": (34, 211, 238),  # Cyan
                "text": (255, 255, 255),
                "shadow": (0, 0, 0)
            },
            {
                "background": [(88, 28, 135), (109, 40, 217)],  # Purple gradient
                "accent": (250, 204, 21),  # Yellow
                "text": (255, 255, 255),
                "shadow": (0, 0, 0)
            },
            {
                "background": [(15, 23, 42), (30, 41, 59)],  # Slate gradient
                "accent": (56, 189, 248),  # Sky blue
                "text": (255, 255, 255),
                "shadow": (0, 0, 0)
            },
            {
                "background": [(20, 83, 45), (22, 101, 52)],  # Green gradient
                "accent": (134, 239, 172),  # Light green
                "text": (255, 255, 255),
                "shadow": (0, 0, 0)
            }
        ]
    
    def create_thumbnail(self, text, subtitle=None, output_path=None):
        """Create a thumbnail with text overlay"""
        print(f"🎨 Creating thumbnail with text: {text}")
        
        # Select random color scheme
        scheme = random.choice(self.color_schemes)
        
        # Create base image with gradient
        img = self._create_gradient_background(scheme["background"])
        
        # Add geometric patterns
        img = self._add_geometric_patterns(img, scheme["accent"])
        
        # Add text
        img = self._add_text(img, text, subtitle, scheme)
        
        # Add border/frame
        img = self._add_border(img, scheme["accent"])
        
        # Save thumbnail
        if not output_path:
            output_path = OUTPUT_DIR / f"thumbnail_{random.randint(1000, 9999)}.png"
        
        img.save(output_path, "PNG", quality=95)
        print(f"✅ Thumbnail saved to: {output_path}")
        
        return output_path
    
    def _create_gradient_background(self, colors):
        """Create a gradient background"""
        img = Image.new('RGB', self.size, colors[0])
        draw = ImageDraw.Draw(img)
        
        # Create vertical gradient
        for i in range(self.size[1]):
            ratio = i / self.size[1]
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, i), (self.size[0], i)], fill=(r, g, b))
        
        return img
    
    def _add_geometric_patterns(self, img, accent_color):
        """Add geometric patterns for visual interest"""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Add semi-transparent circles
        for _ in range(3):
            x = random.randint(0, self.size[0])
            y = random.randint(0, self.size[1])
            radius = random.randint(100, 300)
            
            # Create semi-transparent accent color
            color = accent_color + (30,)  # Add alpha
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=color
            )
        
        # Add diagonal lines
        for i in range(5):
            x = random.randint(0, self.size[0])
            width = random.randint(2, 5)
            color = accent_color + (50,)
            draw.line([(x, 0), (x + 200, self.size[1])], fill=color, width=width)
        
        return img
    
    def _add_text(self, img, main_text, subtitle, scheme):
        """Add text overlay to thumbnail"""
        draw = ImageDraw.Draw(img)
        
        # Try to load custom font, fallback to default
        try:
            # Try to use a bold font
            main_font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 120)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 50)
        except:
            # Fallback to default font
            main_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Wrap text if too long
        main_text = self._wrap_text(main_text, 20)
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), main_text, font=main_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.size[0] - text_width) // 2
        y = (self.size[1] - text_height) // 2 - 50
        
        # Draw shadow
        shadow_offset = 5
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            main_text,
            font=main_font,
            fill=scheme["shadow"],
            align="center"
        )
        
        # Draw main text
        draw.text(
            (x, y),
            main_text,
            font=main_font,
            fill=scheme["text"],
            align="center"
        )
        
        # Add subtitle if provided
        if subtitle:
            subtitle = self._wrap_text(subtitle, 40)
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_width = bbox[2] - bbox[0]
            sub_x = (self.size[0] - sub_width) // 2
            sub_y = y + text_height + 30
            
            # Draw subtitle with background
            padding = 20
            draw.rectangle(
                [sub_x - padding, sub_y - 10, sub_x + sub_width + padding, sub_y + 60],
                fill=scheme["accent"] + (200,)
            )
            
            draw.text(
                (sub_x, sub_y),
                subtitle,
                font=subtitle_font,
                fill=scheme["text"],
                align="center"
            )
        
        return img
    
    def _wrap_text(self, text, max_chars):
        """Wrap text to fit within max characters per line"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "\n".join(lines)
    
    def _add_border(self, img, accent_color):
        """Add a border to the thumbnail"""
        draw = ImageDraw.Draw(img)
        border_width = 8
        
        # Draw border
        draw.rectangle(
            [0, 0, self.size[0] - 1, self.size[1] - 1],
            outline=accent_color,
            width=border_width
        )
        
        return img


def main():
    """Test the thumbnail creator"""
    creator = ThumbnailCreator()
    
    # Test with different texts
    test_cases = [
        ("AI BASICS", "Complete Guide"),
        ("CYBERSECURITY", "Essential Tips"),
        ("CLOUD COMPUTING", "Explained Simply"),
    ]
    
    for main_text, subtitle in test_cases:
        output_path = OUTPUT_DIR / f"test_thumbnail_{main_text.lower().replace(' ', '_')}.png"
        creator.create_thumbnail(main_text, subtitle, output_path)
        print(f"Created: {output_path}\n")


if __name__ == "__main__":
    main()
