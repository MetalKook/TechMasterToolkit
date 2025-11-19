"""
Email Notifier Module
Sends email notifications when videos are published
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import (
    SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, NOTIFICATION_EMAIL
)


class EmailNotifier:
    """Send email notifications"""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.sender_email = SMTP_EMAIL
        self.sender_password = SMTP_PASSWORD
        self.recipient_email = NOTIFICATION_EMAIL or SMTP_EMAIL
    
    def send_success_notification(self, video_data, metadata):
        """Send notification when video is successfully published"""
        print("\n📧 Sending success notification email...")
        
        subject = f"✅ Video Published: {metadata.get('title', 'Untitled')}"
        
        # Create HTML email
        html_content = self._create_success_email_html(video_data, metadata)
        
        # Send email
        success = self._send_email(subject, html_content)
        
        if success:
            print(f"✅ Notification sent to: {self.recipient_email}")
        else:
            print(f"❌ Failed to send notification")
        
        return success
    
    def send_error_notification(self, error_message, stage):
        """Send notification when pipeline fails"""
        print("\n📧 Sending error notification email...")
        
        subject = f"❌ Video Pipeline Failed at {stage}"
        
        # Create HTML email
        html_content = self._create_error_email_html(error_message, stage)
        
        # Send email
        success = self._send_email(subject, html_content)
        
        if success:
            print(f"✅ Error notification sent to: {self.recipient_email}")
        else:
            print(f"❌ Failed to send error notification")
        
        return success
    
    def _send_email(self, subject, html_content):
        """Send email via SMTP"""
        if not all([self.smtp_server, self.sender_email, self.sender_password]):
            print("⚠️ Email configuration incomplete. Skipping notification.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
        
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def _create_success_email_html(self, video_data, metadata):
        """Create HTML content for success notification"""
        video_url = video_data.get('video_url', '#')
        video_id = video_data.get('video_id', 'N/A')
        title = metadata.get('title', 'Untitled')
        description = metadata.get('description', '')[:200] + '...'
        tags = ', '.join(metadata.get('tags', [])[:10])
        hashtags = ' '.join(metadata.get('hashtags', []))
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .video-link {{
                    display: inline-block;
                    background: #FF0000;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .info-box {{
                    background: white;
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .label {{
                    font-weight: bold;
                    color: #667eea;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Video Published Successfully!</h1>
                <p>Your automated video is now live on YouTube</p>
            </div>
            
            <div class="content">
                <div class="info-box">
                    <p class="label">Video Title:</p>
                    <p>{title}</p>
                </div>
                
                <div class="info-box">
                    <p class="label">Video ID:</p>
                    <p>{video_id}</p>
                </div>
                
                <div class="info-box">
                    <p class="label">Description Preview:</p>
                    <p>{description}</p>
                </div>
                
                <div class="info-box">
                    <p class="label">Tags:</p>
                    <p>{tags}</p>
                </div>
                
                <div class="info-box">
                    <p class="label">Hashtags:</p>
                    <p>{hashtags}</p>
                </div>
                
                <center>
                    <a href="{video_url}" class="video-link">▶️ Watch Video on YouTube</a>
                </center>
                
                <div class="info-box">
                    <p class="label">Published:</p>
                    <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from YouTube Automation Pipeline</p>
                <p>Generated by Tech Master Toolkit</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_error_email_html(self, error_message, stage):
        """Create HTML content for error notification"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .error-box {{
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                }}
                .label {{
                    font-weight: bold;
                    color: #f5576c;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>❌ Pipeline Error</h1>
                <p>The video automation pipeline encountered an error</p>
            </div>
            
            <div class="content">
                <div class="error-box">
                    <p class="label">Failed Stage:</p>
                    <p>{stage}</p>
                </div>
                
                <div class="error-box">
                    <p class="label">Error Message:</p>
                    <p>{error_message}</p>
                </div>
                
                <div class="error-box">
                    <p class="label">Time:</p>
                    <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <p><strong>Action Required:</strong></p>
                <ul>
                    <li>Check the logs for detailed error information</li>
                    <li>Verify API credentials and configurations</li>
                    <li>Ensure all dependencies are installed</li>
                    <li>Check network connectivity</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from YouTube Automation Pipeline</p>
                <p>Generated by Tech Master Toolkit</p>
            </div>
        </body>
        </html>
        """
        
        return html


def main():
    """Test the email notifier"""
    notifier = EmailNotifier()
    
    # Test success notification
    test_video_data = {
        'video_id': 'dQw4w9WgXcQ',
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'title': 'Test Video',
        'status': 'success'
    }
    
    test_metadata = {
        'title': 'Understanding AI Basics - Complete Guide',
        'description': 'Learn about artificial intelligence in this comprehensive guide...',
        'tags': ['AI', 'technology', 'tutorial', 'education'],
        'hashtags': ['#AI', '#tech', '#tutorial']
    }
    
    print("Testing Email Notifier...")
    print("\n1. Testing success notification...")
    notifier.send_success_notification(test_video_data, test_metadata)
    
    print("\n2. Testing error notification...")
    notifier.send_error_notification("Test error message", "Video Upload")
    
    print("\n✅ Email notifier test complete")


if __name__ == "__main__":
    main()
