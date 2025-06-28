"""
Audio processing utilities for merging and manipulating audio files
"""

import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional
import os

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handle audio file processing and manipulation"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.temp_dir = Path(tempfile.gettempdir()) / "pdf_audio_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def merge_audio_files(self, audio_files: List[Path], output_path: Path) -> bool:
        """
        Merge multiple audio files into a single file
        
        Args:
            audio_files: List of audio file paths to merge
            output_path: Path for the merged output file
            
        Returns:
            True if successful, False otherwise
        """
        if not audio_files:
            logger.error("No audio files provided for merging")
            return False
        
        if len(audio_files) == 1:
            # If only one file, just copy it
            try:
                with open(audio_files[0], 'rb') as src, open(output_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"Single audio file copied to {output_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to copy single audio file: {str(e)}")
                return False
        
        # Check if ffmpeg is available
        if await self._check_ffmpeg():
            return await self._merge_with_ffmpeg(audio_files, output_path)
        else:
            # Fallback to simple concatenation
            return await self._simple_concatenate(audio_files, output_path)
    
    async def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ffmpeg', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            return result.returncode == 0
        except:
            return False
    
    async def _merge_with_ffmpeg(self, audio_files: List[Path], output_path: Path) -> bool:
        """
        Merge audio files using ffmpeg (high quality)
        
        Args:
            audio_files: List of audio file paths
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Create a temporary file list for ffmpeg
            list_file = self.temp_dir / f"merge_list_{os.getpid()}.txt"
            
            with open(list_file, 'w') as f:
                for audio_file in audio_files:
                    if audio_file.exists():
                        f.write(f"file '{audio_file.absolute()}'\n")
            
            # Use ffmpeg to concatenate
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temp file
            try:
                list_file.unlink()
            except:
                pass
            
            if process.returncode == 0:
                logger.info(f"Successfully merged {len(audio_files)} files with ffmpeg")
                return True
            else:
                logger.error(f"ffmpeg merge failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error merging with ffmpeg: {str(e)}")
            return False
    
    async def _simple_concatenate(self, audio_files: List[Path], output_path: Path) -> bool:
        """
        Simple binary concatenation of MP3 files (fallback method)
        
        Args:
            audio_files: List of audio file paths
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'wb') as output_file:
                for i, audio_file in enumerate(audio_files):
                    if not audio_file.exists():
                        logger.warning(f"Audio file not found: {audio_file}")
                        continue
                    
                    with open(audio_file, 'rb') as input_file:
                        if i == 0:
                            # For first file, copy everything
                            output_file.write(input_file.read())
                        else:
                            # For subsequent files, skip potential headers
                            data = input_file.read()
                            # Simple heuristic: skip first 128 bytes which might contain headers
                            if len(data) > 128:
                                output_file.write(data[128:])
                            else:
                                output_file.write(data)
            
            logger.info(f"Successfully concatenated {len(audio_files)} files (simple method)")
            return True
            
        except Exception as e:
            logger.error(f"Error in simple concatenation: {str(e)}")
            return False
    
    async def get_audio_duration(self, audio_path: Path) -> Optional[float]:
        """
        Get audio file duration in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds, or None if unable to determine
        """
        if not audio_path.exists():
            return None
        
        try:
            # Try using ffprobe if available
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                str(audio_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                duration = float(data['format']['duration'])
                return duration
            
        except:
            pass
        
        # Fallback: estimate based on file size (very rough)
        file_size = audio_path.stat().st_size
        # Rough estimate: 1 minute of MP3 ≈ 1MB at 128kbps
        estimated_duration = file_size / (128 * 1024 / 8)  # bytes per second
        return estimated_duration
    
    async def validate_audio_file(self, audio_path: Path) -> bool:
        """
        Validate that an audio file is properly formatted
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if file appears to be valid audio
        """
        if not audio_path.exists():
            return False
        
        try:
            # Check file size
            if audio_path.stat().st_size < 100:  # Too small to be valid audio
                return False
            
            # Check if it starts with MP3 header
            with open(audio_path, 'rb') as f:
                header = f.read(3)
                # MP3 files typically start with ID3 tag or MP3 frame sync
                if header.startswith(b'ID3') or header[0:2] == b'\xff\xfb':
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating audio file {audio_path}: {str(e)}")
            return False
    
    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
            logger.info("Cleaned up temporary audio files")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
    
    def estimate_processing_time(self, text_length: int) -> float:
        """
        Estimate processing time based on text length
        
        Args:
            text_length: Length of text in characters
            
        Returns:
            Estimated processing time in seconds
        """
        # Rough estimates:
        # - TTS: ~1 second per 100 characters
        # - Audio processing: ~10% of TTS time
        tts_time = text_length / 100
        processing_time = tts_time * 0.1
        total_time = tts_time + processing_time
        
        return max(10, total_time)  # Minimum 10 seconds
