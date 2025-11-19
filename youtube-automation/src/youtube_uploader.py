"""
YouTube Uploader Module
Uploads videos to YouTube using the YouTube Data API v3
"""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import (
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN,
    VIDEO_CATEGORY_ID, VIDEO_PRIVACY, OUTPUT_DIR
)


class YouTubeUploader:
    """Upload videos to YouTube with metadata"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.credentials = None
        self.youtube = None
        self.token_file = OUTPUT_DIR / "youtube_token.pickle"
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        print("🔐 Authenticating with YouTube API...")
        
        # Try to load saved credentials
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("Refreshing access token...")
                self.credentials.refresh(Request())
            else:
                # Use environment variables if available
                if YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET:
                    print("Using credentials from environment variables...")
                    # Create credentials from refresh token
                    if YOUTUBE_REFRESH_TOKEN:
                        self.credentials = Credentials(
                            token=None,
                            refresh_token=YOUTUBE_REFRESH_TOKEN,
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=YOUTUBE_CLIENT_ID,
                            client_secret=YOUTUBE_CLIENT_SECRET,
                            scopes=self.SCOPES
                        )
                        self.credentials.refresh(Request())
                    else:
                        # Need to do OAuth flow
                        print("⚠️ No refresh token found. You need to complete OAuth flow.")
                        print("Please run the setup script to authenticate.")
                        raise ValueError("YouTube authentication required. Run setup first.")
                else:
                    print("⚠️ YouTube credentials not found in environment variables.")
                    raise ValueError("YouTube API credentials not configured.")
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        print("✅ YouTube API authenticated successfully")
    
    def upload_video(self, video_path, metadata, thumbnail_path=None):
        """Upload video to YouTube with metadata"""
        if not self.youtube:
            self.authenticate()
        
        print("\n" + "="*50)
        print("YOUTUBE UPLOAD")
        print("="*50)
        print(f"Video: {video_path}")
        print(f"Title: {metadata.get('title', 'Untitled')}")
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': metadata.get('title', 'Untitled Video'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'categoryId': VIDEO_CATEGORY_ID
            },
            'status': {
                'privacyStatus': VIDEO_PRIVACY,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            # Upload video
            print("📤 Uploading video to YouTube...")
            print("This may take several minutes depending on file size...")
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✅ Video uploaded successfully!")
            print(f"Video ID: {video_id}")
            print(f"Video URL: {video_url}")
            
            # Upload thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                self.upload_thumbnail(video_id, thumbnail_path)
            
            return {
                'video_id': video_id,
                'video_url': video_url,
                'title': metadata.get('title'),
                'status': 'success'
            }
        
        except HttpError as e:
            print(f"❌ YouTube API error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def upload_thumbnail(self, video_id, thumbnail_path):
        """Upload custom thumbnail for video"""
        try:
            print(f"🖼️ Uploading thumbnail...")
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path))
            )
            
            response = request.execute()
            print(f"✅ Thumbnail uploaded successfully")
            return response
        
        except HttpError as e:
            print(f"⚠️ Thumbnail upload failed: {e}")
            print("Note: Custom thumbnails require verified YouTube account")
            return None
    
    def update_video_metadata(self, video_id, metadata):
        """Update video metadata after upload"""
        try:
            # Get current video details
            video = self.youtube.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            if not video['items']:
                print(f"❌ Video {video_id} not found")
                return None
            
            # Update metadata
            video_data = video['items'][0]
            video_data['snippet']['title'] = metadata.get('title', video_data['snippet']['title'])
            video_data['snippet']['description'] = metadata.get('description', video_data['snippet']['description'])
            video_data['snippet']['tags'] = metadata.get('tags', video_data['snippet'].get('tags', []))
            
            # Update video
            response = self.youtube.videos().update(
                part='snippet,status',
                body=video_data
            ).execute()
            
            print(f"✅ Video metadata updated")
            return response
        
        except HttpError as e:
            print(f"❌ Metadata update failed: {e}")
            return None


def setup_youtube_auth():
    """Setup script to get YouTube OAuth credentials"""
    print("="*50)
    print("YOUTUBE API SETUP")
    print("="*50)
    print("\nThis script will help you authenticate with YouTube API.")
    print("\nPrerequisites:")
    print("1. Create a project in Google Cloud Console")
    print("2. Enable YouTube Data API v3")
    print("3. Create OAuth 2.0 credentials (Desktop app)")
    print("4. Download the credentials JSON file")
    print("\nVisit: https://console.cloud.google.com/apis/credentials")
    
    credentials_path = input("\nEnter path to your credentials JSON file: ").strip()
    
    if not Path(credentials_path).exists():
        print("❌ Credentials file not found!")
        return
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    
    credentials = flow.run_local_server(port=8080)
    
    # Save credentials
    token_file = OUTPUT_DIR / "youtube_token.pickle"
    with open(token_file, 'wb') as token:
        pickle.dump(credentials, token)
    
    print(f"\n✅ Authentication successful!")
    print(f"Token saved to: {token_file}")
    print(f"\nRefresh token: {credentials.refresh_token}")
    print("\nAdd this to your .env file:")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")


def main():
    """Test or setup YouTube uploader"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_youtube_auth()
    else:
        print("YouTube Uploader Module")
        print("\nTo setup authentication, run:")
        print("python youtube_uploader.py setup")
        print("\nOr configure credentials in .env file:")
        print("- YOUTUBE_CLIENT_ID")
        print("- YOUTUBE_CLIENT_SECRET")
        print("- YOUTUBE_REFRESH_TOKEN")


if __name__ == "__main__":
    main()
