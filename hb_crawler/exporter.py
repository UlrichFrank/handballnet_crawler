"""Export module for saving extracted data"""

import json
import csv
from typing import List, Dict, Any
from pathlib import Path


class DataExporter:
    """Exports crawled data to various formats"""
    
    @staticmethod
    def to_json(data: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export data to JSON format
        
        Args:
            data: List of data dictionaries
            output_file: Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Data exported to {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def to_csv(data: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export data to CSV format
        
        Args:
            data: List of data dictionaries
            output_file: Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not data:
            print("✗ No data to export")
            return False
        
        try:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            fieldnames = set()
            for record in data:
                fieldnames.update(record.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"✓ Data exported to {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to CSV: {e}")
            return False
