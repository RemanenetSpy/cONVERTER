"""
File Size Reducer Module
Compresses and optimizes files to reduce size while maintaining quality
"""

import os
from typing import Dict, Any, Optional
from PIL import Image
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd


class FileSizeReducer:
    """Reduces file sizes through compression and optimization"""

    @staticmethod
    def compress_image(
        input_path: str,
        output_path: str,
        quality: int = 85,
        max_dimension: Optional[int] = None
    ) -> Dict[str, Any]:
        """Compress image file"""
        
        try:
            img = Image.open(input_path)
            original_size = os.path.getsize(input_path)
            
            # Resize if max dimension specified
            if max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB if saving as JPEG
            if img.mode in ('RGBA', 'LA', 'P') and output_path.lower().endswith(('.jpg', '.jpeg')):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode != 'P' else None)
                img = background
            
            # Save with compression
            save_kwargs = {'optimize': True}
            
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
            elif output_path.lower().endswith('.png'):
                save_kwargs['compress_level'] = 9
            elif output_path.lower().endswith('.webp'):
                save_kwargs['quality'] = quality
                save_kwargs['method'] = 6
            
            img.save(output_path, **save_kwargs)
            
            compressed_size = os.path.getsize(output_path)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
            return {
                "success": True,
                "message": f"Compressed image by {reduction_percent:.1f}%",
                "originalSize": original_size,
                "compressedSize": compressed_size,
                "reductionPercent": round(reduction_percent, 2),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Image compression failed: {str(e)}")

    @staticmethod
    def compress_pdf(
        input_path: str,
        output_path: str,
        compression_level: str = "medium"
    ) -> Dict[str, Any]:
        """Compress PDF file"""
        
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            original_size = os.path.getsize(input_path)
            
            # Add all pages
            for page in reader.pages:
                # Compress page content
                page.compress_content_streams()
                writer.add_page(page)
            
            # Set compression level
            if compression_level == "high":
                writer.add_metadata(reader.metadata)
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
            return {
                "success": True,
                "message": f"Compressed PDF by {reduction_percent:.1f}%",
                "originalSize": original_size,
                "compressedSize": compressed_size,
                "reductionPercent": round(reduction_percent, 2),
                "pages": len(reader.pages),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"PDF compression failed: {str(e)}")

    @staticmethod
    def compress_excel(
        input_path: str,
        output_path: str,
        remove_formatting: bool = False
    ) -> Dict[str, Any]:
        """Compress Excel file by removing unnecessary data"""
        
        try:
            original_size = os.path.getsize(input_path)
            
            # Read Excel file
            df = pd.read_excel(input_path)
            
            # Remove empty rows and columns
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            
            # Save with compression
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            compressed_size = os.path.getsize(output_path)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
            return {
                "success": True,
                "message": f"Compressed Excel by {reduction_percent:.1f}%",
                "originalSize": original_size,
                "compressedSize": compressed_size,
                "reductionPercent": round(reduction_percent, 2),
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Excel compression failed: {str(e)}")

    @staticmethod
    def compress_csv(
        input_path: str,
        output_path: str,
        remove_duplicates: bool = False
    ) -> Dict[str, Any]:
        """Compress CSV file"""
        
        try:
            original_size = os.path.getsize(input_path)
            
            # Read CSV
            df = pd.read_csv(input_path)
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            # Optionally remove duplicates
            if remove_duplicates:
                original_rows = len(df)
                df = df.drop_duplicates()
                removed_rows = original_rows - len(df)
            
            # Save compressed
            df.to_csv(output_path, index=False, compression='gzip' if output_path.endswith('.gz') else None)
            
            compressed_size = os.path.getsize(output_path)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
            result = {
                "success": True,
                "message": f"Compressed CSV by {reduction_percent:.1f}%",
                "originalSize": original_size,
                "compressedSize": compressed_size,
                "reductionPercent": round(reduction_percent, 2),
                "rows": len(df),
                "outputPath": output_path
            }
            
            if remove_duplicates:
                result["duplicatesRemoved"] = removed_rows
            
            return result
        
        except Exception as e:
            raise Exception(f"CSV compression failed: {str(e)}")

    @staticmethod
    def get_file_size_info(file_path: str) -> Dict[str, Any]:
        """Get detailed file size information"""
        
        try:
            size_bytes = os.path.getsize(file_path)
            
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    size_str = f"{size_bytes:.2f} {unit}"
                    break
                size_bytes /= 1024.0
            else:
                size_str = f"{size_bytes:.2f} TB"
            
            return {
                "success": True,
                "path": file_path,
                "sizeBytes": os.path.getsize(file_path),
                "sizeFormatted": size_str
            }
        
        except Exception as e:
            raise Exception(f"File size info failed: {str(e)}")

    @staticmethod
    def batch_compress_images(
        input_paths: list,
        output_dir: str,
        quality: int = 85
    ) -> Dict[str, Any]:
        """Compress multiple images at once"""
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            results = []
            total_original = 0
            total_compressed = 0
            
            for input_path in input_paths:
                filename = os.path.basename(input_path)
                output_path = os.path.join(output_dir, filename)
                
                try:
                    result = FileSizeReducer.compress_image(input_path, output_path, quality)
                    results.append(result)
                    total_original += result["originalSize"]
                    total_compressed += result["compressedSize"]
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "file": filename
                    })
            
            total_reduction = ((total_original - total_compressed) / total_original) * 100 if total_original > 0 else 0
            
            return {
                "success": True,
                "message": f"Compressed {len(input_paths)} images",
                "totalOriginalSize": total_original,
                "totalCompressedSize": total_compressed,
                "totalReductionPercent": round(total_reduction, 2),
                "results": results,
                "outputDir": output_dir
            }
        
        except Exception as e:
            raise Exception(f"Batch compression failed: {str(e)}")
