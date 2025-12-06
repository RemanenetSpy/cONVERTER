"""
Audio Converter Module
Handles audio format conversions using pydub and FFmpeg
"""

import os
from typing import Dict, Any
from pathlib import Path


class AudioConverter:
    """Converts audio files between formats"""

    SUPPORTED_FORMATS = ["mp3", "wav", "aac", "ogg", "m4a", "flac"]

    @staticmethod
    def convert(
        input_path: str,
        output_path: str,
        target_format: str,
        bitrate: str = "320k"
    ) -> Dict[str, Any]:
        """Convert audio to another format"""
        
        try:
            from pydub import AudioSegment
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Export with format-specific settings
            export_params = {
                "format": target_format,
                "bitrate": bitrate
            }
            
            # Format-specific optimizations
            if target_format == "mp3":
                export_params["parameters"] = ["-q:a", "0"]  # Extreme quality
            elif target_format == "wav":
                export_params.pop("bitrate")  # WAV doesn't use bitrate
            elif target_format == "ogg":
                export_params["codec"] = "libvorbis"
            
            audio.export(output_path, **export_params)
            
            # Get metadata
            output_size = os.path.getsize(output_path)
            duration_ms = len(audio)
            
            return {
                "success": True,
                "message": f"Converted to {target_format.upper()}",
                "outputPath": output_path,
                "format": target_format,
                "duration": duration_ms / 1000,  # Convert to seconds
                "bitrate": bitrate if target_format != "wav" else "N/A",
                "fileSize": output_size,
                "channels": audio.channels,
                "sampleRate": audio.frame_rate
            }
        
        except ImportError:
            raise Exception("pydub library not installed. Install with: pip install pydub")
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")

    @staticmethod
    def mp3_to_wav(input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert MP3 to WAV"""
        return AudioConverter.convert(input_path, output_path, "wav")

    @staticmethod
    def wav_to_mp3(input_path: str, output_path: str, bitrate: str = "320k") -> Dict[str, Any]:
        """Convert WAV to MP3"""
        return AudioConverter.convert(input_path, output_path, "mp3", bitrate)

    @staticmethod
    def aac_to_mp3(input_path: str, output_path: str, bitrate: str = "320k") -> Dict[str, Any]:
        """Convert AAC to MP3"""
        return AudioConverter.convert(input_path, output_path, "mp3", bitrate)

    @staticmethod
    def ogg_to_mp3(input_path: str, output_path: str, bitrate: str = "320k") -> Dict[str, Any]:
        """Convert OGG to MP3"""
        return AudioConverter.convert(input_path, output_path, "mp3", bitrate)

    @staticmethod
    def m4a_to_mp3(input_path: str, output_path: str, bitrate: str = "320k") -> Dict[str, Any]:
        """Convert M4A to MP3"""
        return AudioConverter.convert(input_path, output_path, "mp3", bitrate)

    @staticmethod
    def get_audio_info(audio_path: str) -> Dict[str, Any]:
        """Get audio file metadata"""
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(audio_path)
            file_size = os.path.getsize(audio_path)
            
            return {
                "success": True,
                "path": audio_path,
                "format": Path(audio_path).suffix[1:].upper(),
                "duration": len(audio) / 1000,  # seconds
                "channels": audio.channels,
                "sampleRate": audio.frame_rate,
                "bitDepth": audio.sample_width * 8,
                "fileSize": file_size,
                "fileSizeMB": round(file_size / (1024 * 1024), 2)
            }
        
        except Exception as e:
            raise Exception(f"Audio info extraction failed: {str(e)}")

    @staticmethod
    def adjust_volume(
        input_path: str,
        output_path: str,
        volume_change_db: float
    ) -> Dict[str, Any]:
        """Adjust audio volume"""
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(input_path)
            adjusted = audio + volume_change_db  # Increase/decrease volume
            
            output_format = Path(output_path).suffix[1:]
            adjusted.export(output_path, format=output_format)
            
            return {
                "success": True,
                "message": f"Volume adjusted by {volume_change_db}dB",
                "outputPath": output_path,
                "volumeChange": volume_change_db
            }
        
        except Exception as e:
            raise Exception(f"Volume adjustment failed: {str(e)}")

    @staticmethod
    def trim_audio(
        input_path: str,
        output_path: str,
        start_ms: int,
        end_ms: int
    ) -> Dict[str, Any]:
        """Trim audio file"""
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(input_path)
            trimmed = audio[start_ms:end_ms]
            
            output_format = Path(output_path).suffix[1:]
            trimmed.export(output_path, format=output_format)
            
            return {
                "success": True,
                "message": f"Trimmed audio ({(end_ms - start_ms) / 1000}s)",
                "outputPath": output_path,
                "duration": len(trimmed) / 1000
            }
        
        except Exception as e:
            raise Exception(f"Audio trimming failed: {str(e)}")

    @staticmethod
    def merge_audio(
        input_paths: list,
        output_path: str
    ) -> Dict[str, Any]:
        """Merge multiple audio files"""
        
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            
            for path in input_paths:
                audio = AudioSegment.from_file(path)
                combined += audio
            
            output_format = Path(output_path).suffix[1:]
            combined.export(output_path, format=output_format)
            
            return {
                "success": True,
                "message": f"Merged {len(input_paths)} audio files",
                "outputPath": output_path,
                "duration": len(combined) / 1000,
                "files": len(input_paths)
            }
        
        except Exception as e:
            raise Exception(f"Audio merging failed: {str(e)}")
