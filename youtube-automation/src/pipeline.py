"""
Main Pipeline Orchestrator
Coordinates the entire video generation and upload process
"""
import json
import logging
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from content_generator import ContentGenerator
from seo_optimizer import SEOOptimizer
from thumbnail_creator import ThumbnailCreator
from audio_producer import AudioProducer
from video_editor import VideoEditor
from youtube_uploader import YouTubeUploader
from email_notifier import EmailNotifier
from config.settings import OUTPUT_DIR, LOGS_DIR


class VideoPipeline:
    """Orchestrate the complete video generation pipeline"""
    
    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all modules
        self.logger.info("Initializing pipeline modules...")
        self.content_gen = ContentGenerator()
        self.seo_optimizer = SEOOptimizer()
        self.thumbnail_creator = ThumbnailCreator()
        self.audio_producer = AudioProducer()
        self.video_editor = VideoEditor()
        self.youtube_uploader = YouTubeUploader()
        self.email_notifier = EmailNotifier()
        
        self.logger.info("✅ All modules initialized")
    
    def setup_logging(self, log_level):
        """Setup logging configuration"""
        log_file = LOGS_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def run(self, topic=None, upload=True, send_email=True):
        """Run the complete pipeline"""
        self.logger.info("="*60)
        self.logger.info("STARTING YOUTUBE AUTOMATION PIPELINE")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        results = {
            'status': 'running',
            'start_time': start_time.isoformat(),
            'stages': {}
        }
        
        try:
            # Stage 1: Generate Content
            self.logger.info("\n📝 STAGE 1: Content Generation")
            script_data = self._generate_content(topic)
            results['stages']['content_generation'] = {'status': 'success', 'data': script_data}
            
            # Stage 2: Generate SEO Metadata
            self.logger.info("\n🔍 STAGE 2: SEO Optimization")
            metadata = self._generate_seo(script_data)
            results['stages']['seo_optimization'] = {'status': 'success', 'data': metadata}
            
            # Stage 3: Create Thumbnail
            self.logger.info("\n🎨 STAGE 3: Thumbnail Creation")
            thumbnail_path = self._create_thumbnail(metadata)
            results['stages']['thumbnail_creation'] = {'status': 'success', 'path': str(thumbnail_path)}
            
            # Stage 4: Generate Audio
            self.logger.info("\n🎙️ STAGE 4: Audio Production")
            audio_path, duration = self._generate_audio(script_data)
            results['stages']['audio_production'] = {'status': 'success', 'path': str(audio_path), 'duration': duration}
            
            # Stage 5: Create Video
            self.logger.info("\n🎬 STAGE 5: Video Editing")
            video_path = self._create_video(audio_path, thumbnail_path, script_data)
            results['stages']['video_editing'] = {'status': 'success', 'path': str(video_path)}
            
            # Stage 6: Upload to YouTube
            if upload:
                self.logger.info("\n📤 STAGE 6: YouTube Upload")
                upload_result = self._upload_to_youtube(video_path, metadata, thumbnail_path)
                results['stages']['youtube_upload'] = upload_result
                
                # Stage 7: Send Email Notification
                if send_email and upload_result.get('status') == 'success':
                    self.logger.info("\n📧 STAGE 7: Email Notification")
                    self._send_notification(upload_result, metadata)
                    results['stages']['email_notification'] = {'status': 'success'}
            else:
                self.logger.info("\n⏭️ Skipping YouTube upload (upload=False)")
                results['stages']['youtube_upload'] = {'status': 'skipped'}
            
            # Pipeline completed successfully
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results['status'] = 'success'
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
            self.logger.info("\n" + "="*60)
            self.logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info(f"Total duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            self.logger.info("="*60)
            
            # Save results
            self._save_results(results)
            
            return results
        
        except Exception as e:
            self.logger.error(f"\n❌ PIPELINE FAILED: {e}", exc_info=True)
            
            results['status'] = 'error'
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()
            
            # Send error notification
            if send_email:
                try:
                    stage = self._get_failed_stage(results)
                    self.email_notifier.send_error_notification(str(e), stage)
                except:
                    pass
            
            self._save_results(results)
            raise
    
    def _generate_content(self, topic=None):
        """Generate video script"""
        try:
            script_data = self.content_gen.generate_script(topic)
            self.content_gen.save_script(script_data)
            self.logger.info(f"✅ Script generated: {script_data.get('topic')}")
            return script_data
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    def _generate_seo(self, script_data):
        """Generate SEO metadata"""
        try:
            metadata = self.seo_optimizer.generate_metadata(script_data)
            thumbnail_text = self.seo_optimizer.generate_thumbnail_text(metadata)
            metadata['thumbnail_text'] = thumbnail_text
            self.seo_optimizer.save_metadata(metadata)
            self.logger.info(f"✅ SEO metadata generated")
            return metadata
        except Exception as e:
            self.logger.error(f"SEO optimization failed: {e}")
            raise
    
    def _create_thumbnail(self, metadata):
        """Create video thumbnail"""
        try:
            thumbnail_text = metadata.get('thumbnail_text', metadata.get('title', 'VIDEO'))
            # Extract subtitle from title if possible
            title_words = metadata.get('title', '').split()
            subtitle = ' '.join(title_words[-3:]) if len(title_words) > 3 else None
            
            thumbnail_path = self.thumbnail_creator.create_thumbnail(
                thumbnail_text,
                subtitle
            )
            self.logger.info(f"✅ Thumbnail created: {thumbnail_path}")
            return thumbnail_path
        except Exception as e:
            self.logger.error(f"Thumbnail creation failed: {e}")
            raise
    
    def _generate_audio(self, script_data):
        """Generate audio with TTS and music"""
        try:
            text = self.content_gen.format_script_for_tts(script_data)
            audio_path, duration = self.audio_producer.create_full_audio(text)
            self.logger.info(f"✅ Audio generated: {duration:.1f}s")
            return audio_path, duration
        except Exception as e:
            self.logger.error(f"Audio production failed: {e}")
            raise
    
    def _create_video(self, audio_path, thumbnail_path, script_data):
        """Create final video"""
        try:
            video_path = self.video_editor.create_video(
                audio_path,
                thumbnail_path,
                script_data
            )
            self.logger.info(f"✅ Video created: {video_path}")
            return video_path
        except Exception as e:
            self.logger.error(f"Video editing failed: {e}")
            raise
    
    def _upload_to_youtube(self, video_path, metadata, thumbnail_path):
        """Upload video to YouTube"""
        try:
            result = self.youtube_uploader.upload_video(
                video_path,
                metadata,
                thumbnail_path
            )
            
            if result.get('status') == 'success':
                self.logger.info(f"✅ Video uploaded: {result.get('video_url')}")
            else:
                self.logger.error(f"Upload failed: {result.get('error')}")
            
            return result
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _send_notification(self, upload_result, metadata):
        """Send email notification"""
        try:
            self.email_notifier.send_success_notification(upload_result, metadata)
            self.logger.info("✅ Email notification sent")
        except Exception as e:
            self.logger.warning(f"Email notification failed: {e}")
    
    def _get_failed_stage(self, results):
        """Determine which stage failed"""
        stages = results.get('stages', {})
        for stage_name, stage_data in stages.items():
            if stage_data.get('status') == 'error':
                return stage_name
        return 'Unknown'
    
    def _save_results(self, results):
        """Save pipeline results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = OUTPUT_DIR / f"pipeline_results_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Results saved to: {results_file}")
        except Exception as e:
            self.logger.warning(f"Could not save results: {e}")


def main():
    """Run the pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Automation Pipeline')
    parser.add_argument('--topic', type=str, help='Video topic (optional, will auto-generate if not provided)')
    parser.add_argument('--no-upload', action='store_true', help='Skip YouTube upload')
    parser.add_argument('--no-email', action='store_true', help='Skip email notification')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set log level
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    # Create and run pipeline
    pipeline = VideoPipeline(log_level=log_level)
    
    try:
        results = pipeline.run(
            topic=args.topic,
            upload=not args.no_upload,
            send_email=not args.no_email
        )
        
        print("\n" + "="*60)
        print("PIPELINE SUMMARY")
        print("="*60)
        print(f"Status: {results['status']}")
        print(f"Duration: {results.get('duration_seconds', 0):.1f}s")
        
        if results.get('status') == 'success':
            upload_data = results['stages'].get('youtube_upload', {})
            if upload_data.get('video_url'):
                print(f"\n🎉 Video URL: {upload_data['video_url']}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
