"""
Document Converter Module
Handles CSV, Excel, Parquet, and PDF conversions
"""

import os
import csv
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pathlib import Path


class DocumentConverter:
    """Converts between document formats"""

    @staticmethod
    def excel_to_csv(
        input_path: str,
        output_path: str,
        sheet_index: int = 0
    ) -> Dict[str, Any]:
        """Convert Excel to CSV"""
        
        try:
            df = pd.read_excel(input_path, sheet_name=sheet_index)
            df.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Converted sheet to CSV",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Excel to CSV conversion failed: {str(e)}")

    @staticmethod
    def csv_to_excel(
        input_path: str,
        output_path: str,
        sheet_name: str = "Sheet1"
    ) -> Dict[str, Any]:
        """Convert CSV to Excel"""
        
        try:
            df = pd.read_csv(input_path)
            df.to_excel(output_path, sheet_name=sheet_name, index=False)
            
            return {
                "success": True,
                "message": f"Converted CSV to Excel",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"CSV to Excel conversion failed: {str(e)}")

    @staticmethod
    def csv_to_parquet(
        input_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Convert CSV to Parquet"""
        
        try:
            df = pd.read_csv(input_path)
            df.to_parquet(output_path, compression="snappy")
            
            return {
                "success": True,
                "message": "Converted CSV to Parquet",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"CSV to Parquet conversion failed: {str(e)}")

    @staticmethod
    def excel_to_parquet(
        input_path: str,
        output_path: str,
        sheet_index: int = 0
    ) -> Dict[str, Any]:
        """Convert Excel to Parquet"""
        
        try:
            df = pd.read_excel(input_path, sheet_name=sheet_index)
            df.to_parquet(output_path, compression="snappy")
            
            return {
                "success": True,
                "message": "Converted Excel to Parquet",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Excel to Parquet conversion failed: {str(e)}")

    @staticmethod
    def parquet_to_csv(
        input_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Convert Parquet to CSV"""
        
        try:
            df = pd.read_parquet(input_path)
            df.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": "Converted Parquet to CSV",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Parquet to CSV conversion failed: {str(e)}")

    @staticmethod
    def validate_csv(
        csv_path: str,
        required_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate CSV structure"""
        
        try:
            df = pd.read_csv(csv_path)
            validation = {
                "valid": True,
                "errors": [],
                "rowCount": len(df),
                "columnCount": len(df.columns),
                "columns": df.columns.tolist()
            }
            
            # Check required columns
            if required_columns:
                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing columns: {', '.join(missing)}")
            
            # Check for empty rows
            if df.isnull().all(axis=1).any():
                validation["warnings"] = ["Contains empty rows"]
            
            return validation
        
        except Exception as e:
            raise Exception(f"CSV validation failed: {str(e)}")

    @staticmethod
    def count_csv_rows(csv_path: str) -> int:
        """Count rows in CSV file"""
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in csv.reader(f)) - 1  # Subtract header
        
        except Exception as e:
            raise Exception(f"Row count failed: {str(e)}")

    @staticmethod
    def merge_excel_files(
        input_paths: List[str],
        output_path: str,
        sheet_name_prefix: str = "Sheet"
    ) -> Dict[str, Any]:
        """Merge multiple Excel files into one"""
        
        try:
            with pd.ExcelWriter(output_path) as writer:
                for i, input_path in enumerate(input_paths):
                    df = pd.read_excel(input_path)
                    sheet_name = f"{sheet_name_prefix}_{i + 1}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return {
                "success": True,
                "message": f"Merged {len(input_paths)} Excel files",
                "sheetsCreated": len(input_paths),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Excel merge failed: {str(e)}")

    @staticmethod
    def split_excel_by_sheets(
        input_path: str,
        output_dir: str,
        include_sheets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Split Excel file by sheets into separate files"""
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            excel_file = pd.ExcelFile(input_path)
            sheets = include_sheets or excel_file.sheet_names
            output_files = []
            
            for sheet_name in sheets:
                if sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(input_path, sheet_name=sheet_name)
                    output_path = os.path.join(output_dir, f"{sheet_name}.xlsx")
                    df.to_excel(output_path, index=False)
                    output_files.append(output_path)
            
            return {
                "success": True,
                "message": f"Split into {len(output_files)} files",
                "files": output_files,
                "outputDir": output_dir
            }
        
        except Exception as e:
            raise Exception(f"Excel split failed: {str(e)}")

    @staticmethod
    def extract_csv_rows(
        input_path: str,
        output_path: str,
        start_row: int = 1,
        end_row: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extract specific rows from CSV"""
        
        try:
            df = pd.read_csv(input_path)
            end_row = end_row or len(df)
            extracted_df = df.iloc[start_row - 1:end_row]
            extracted_df.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Extracted {len(extracted_df)} rows",
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"CSV extraction failed: {str(e)}")

    @staticmethod
    def batch_convert_csv_to_excel(
        input_paths: List[str],
        output_dir: str
    ) -> Dict[str, Any]:
        """Batch convert multiple CSV files to Excel"""
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for input_path in input_paths:
            try:
                basename = Path(input_path).stem
                output_path = os.path.join(output_dir, f"{basename}.xlsx")
                
                result = DocumentConverter.csv_to_excel(input_path, output_path)
                results.append(result)
            
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "inputPath": input_path
                })
        
        return {
            "success": True,
            "message": f"Batch converted {len(results)} CSV files",
            "total": len(input_paths),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "results": results,
            "outputDir": output_dir
        }

    @staticmethod
    def get_statistics(csv_path: str) -> Dict[str, Any]:
        """Get statistical information about CSV data"""
        
        try:
            df = pd.read_csv(csv_path)
            stats = {
                "rowCount": len(df),
                "columnCount": len(df.columns),
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "nullCounts": df.isnull().sum().to_dict(),
                "numericStats": {}
            }
            
            # Add numeric statistics
            for col in df.select_dtypes(include=[np.number]).columns:
                stats["numericStats"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            
            return stats
        
        except Exception as e:
            raise Exception(f"Statistics generation failed: {str(e)}")

    @staticmethod
    def csv_to_json(input_path: str, output_path: str, orient: str = "records") -> Dict[str, Any]:
        """Convert CSV to JSON"""
        
        try:
            df = pd.read_csv(input_path)
            df.to_json(output_path, orient=orient, indent=2)
            
            return {
                "success": True,
                "message": "Converted CSV to JSON",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"CSV to JSON conversion failed: {str(e)}")

    @staticmethod
    def json_to_csv(input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert JSON to CSV"""
        
        try:
            df = pd.read_json(input_path)
            df.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": "Converted JSON to CSV",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"JSON to CSV conversion failed: {str(e)}")

    @staticmethod
    def excel_to_json(input_path: str, output_path: str, sheet_index: int = 0) -> Dict[str, Any]:
        """Convert Excel to JSON"""
        
        try:
            df = pd.read_excel(input_path, sheet_name=sheet_index)
            df.to_json(output_path, orient="records", indent=2)
            
            return {
                "success": True,
                "message": "Converted Excel to JSON",
                "rows": len(df),
                "columns": len(df.columns),
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Excel to JSON conversion failed: {str(e)}")
