"""
Archive Converter Module
Handles archive format conversions and operations
"""

import os
import zipfile
import tarfile
import py7zr
from typing import Dict, Any, List
from pathlib import Path


class ArchiveConverter:
    """Converts and manages archive files"""

    SUPPORTED_FORMATS = ["zip", "7z", "tar", "tar.gz", "tar.bz2"]

    @staticmethod
    def zip_to_7z(input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert ZIP to 7Z"""
        
        try:
            # Create temp directory for extraction
            temp_dir = f"{input_path}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract ZIP
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                file_count = len(zip_ref.namelist())
            
            # Create 7Z
            with py7zr.SevenZipFile(output_path, 'w') as archive:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        archive.write(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
            original_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": "Converted ZIP to 7Z",
                "outputPath": output_path,
                "files": file_count,
                "originalSize": original_size,
                "outputSize": output_size,
                "compressionRatio": round((1 - output_size / original_size) * 100, 2) if original_size > 0 else 0
            }
        
        except Exception as e:
            raise Exception(f"ZIP to 7Z conversion failed: {str(e)}")

    @staticmethod
    def seven_z_to_zip(input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert 7Z to ZIP"""
        
        try:
            # Create temp directory for extraction
            temp_dir = f"{input_path}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract 7Z
            with py7zr.SevenZipFile(input_path, 'r') as archive:
                archive.extractall(temp_dir)
                file_count = len(archive.getnames())
            
            # Create ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_ref.write(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
            original_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": "Converted 7Z to ZIP",
                "outputPath": output_path,
                "files": file_count,
                "originalSize": original_size,
                "outputSize": output_size
            }
        
        except Exception as e:
            raise Exception(f"7Z to ZIP conversion failed: {str(e)}")

    @staticmethod
    def tar_to_zip(input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert TAR to ZIP"""
        
        try:
            # Create temp directory for extraction
            temp_dir = f"{input_path}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract TAR
            with tarfile.open(input_path, 'r:*') as tar_ref:
                tar_ref.extractall(temp_dir)
                file_count = len(tar_ref.getnames())
            
            # Create ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_ref.write(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
            original_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": "Converted TAR to ZIP",
                "outputPath": output_path,
                "files": file_count,
                "originalSize": original_size,
                "outputSize": output_size
            }
        
        except Exception as e:
            raise Exception(f"TAR to ZIP conversion failed: {str(e)}")

    @staticmethod
    def zip_to_tar(input_path: str, output_path: str, compression: str = "gz") -> Dict[str, Any]:
        """Convert ZIP to TAR"""
        
        try:
            # Create temp directory for extraction
            temp_dir = f"{input_path}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract ZIP
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                file_count = len(zip_ref.namelist())
            
            # Create TAR
            mode = f"w:{compression}" if compression else "w"
            with tarfile.open(output_path, mode) as tar_ref:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        tar_ref.add(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
            original_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": f"Converted ZIP to TAR.{compression.upper()}",
                "outputPath": output_path,
                "files": file_count,
                "originalSize": original_size,
                "outputSize": output_size
            }
        
        except Exception as e:
            raise Exception(f"ZIP to TAR conversion failed: {str(e)}")

    @staticmethod
    def extract_archive(input_path: str, output_dir: str) -> Dict[str, Any]:
        """Extract any supported archive format"""
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            ext = Path(input_path).suffix.lower()
            
            if ext == '.zip':
                with zipfile.ZipFile(input_path, 'r') as archive:
                    archive.extractall(output_dir)
                    file_count = len(archive.namelist())
            elif ext == '.7z':
                with py7zr.SevenZipFile(input_path, 'r') as archive:
                    archive.extractall(output_dir)
                    file_count = len(archive.getnames())
            elif ext in ['.tar', '.gz', '.bz2'] or input_path.endswith('.tar.gz') or input_path.endswith('.tar.bz2'):
                with tarfile.open(input_path, 'r:*') as archive:
                    archive.extractall(output_dir)
                    file_count = len(archive.getnames())
            else:
                raise Exception(f"Unsupported archive format: {ext}")
            
            return {
                "success": True,
                "message": f"Extracted {file_count} files",
                "outputDir": output_dir,
                "files": file_count
            }
        
        except Exception as e:
            raise Exception(f"Archive extraction failed: {str(e)}")

    @staticmethod
    def create_archive(
        file_paths: List[str],
        output_path: str,
        archive_type: str = "zip"
    ) -> Dict[str, Any]:
        """Create archive from multiple files"""
        
        try:
            if archive_type == "zip":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for file_path in file_paths:
                        archive.write(file_path, os.path.basename(file_path))
            elif archive_type == "7z":
                with py7zr.SevenZipFile(output_path, 'w') as archive:
                    for file_path in file_paths:
                        archive.write(file_path, os.path.basename(file_path))
            elif archive_type == "tar":
                with tarfile.open(output_path, 'w:gz') as archive:
                    for file_path in file_paths:
                        archive.add(file_path, os.path.basename(file_path))
            else:
                raise Exception(f"Unsupported archive type: {archive_type}")
            
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": f"Created {archive_type.upper()} archive with {len(file_paths)} files",
                "outputPath": output_path,
                "files": len(file_paths),
                "size": output_size
            }
        
        except Exception as e:
            raise Exception(f"Archive creation failed: {str(e)}")

    @staticmethod
    def get_archive_info(archive_path: str) -> Dict[str, Any]:
        """Get archive metadata"""
        
        try:
            ext = Path(archive_path).suffix.lower()
            file_size = os.path.getsize(archive_path)
            
            if ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as archive:
                    file_list = archive.namelist()
                    file_count = len(file_list)
            elif ext == '.7z':
                with py7zr.SevenZipFile(archive_path, 'r') as archive:
                    file_list = archive.getnames()
                    file_count = len(file_list)
            elif ext in ['.tar', '.gz', '.bz2']:
                with tarfile.open(archive_path, 'r:*') as archive:
                    file_list = archive.getnames()
                    file_count = len(file_list)
            else:
                raise Exception(f"Unsupported archive format: {ext}")
            
            return {
                "success": True,
                "path": archive_path,
                "format": ext[1:].upper(),
                "fileCount": file_count,
                "fileSize": file_size,
                "fileSizeMB": round(file_size / (1024 * 1024), 2),
                "files": file_list[:10]  # First 10 files
            }
        
        except Exception as e:
            raise Exception(f"Archive info extraction failed: {str(e)}")
