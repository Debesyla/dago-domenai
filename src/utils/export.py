"""
Export utilities for domain analysis results.
Supports JSON and CSV formats with customizable output paths.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ResultExporter:
    """Handles exporting domain analysis results to various formats."""
    
    def __init__(self, export_dir: str = "exports", logger=None):
        """
        Initialize the exporter.
        
        Args:
            export_dir: Directory to store export files (default: 'exports')
            logger: Custom logger instance (optional, creates default if None)
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        self.logger = logger if logger else logging.getLogger(__name__)
        
    def generate_filename(self, prefix: str = "results", extension: str = "json") -> str:
        """
        Generate timestamped filename.
        
        Args:
            prefix: Filename prefix (default: 'results')
            extension: File extension without dot (default: 'json')
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_json(
        self, 
        results: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        indent: int = 2
    ) -> Path:
        """
        Export results to JSON file.
        
        Args:
            results: List of domain result dictionaries
            filename: Custom filename (optional, auto-generated if None)
            indent: JSON indentation level (default: 2)
            
        Returns:
            Path to the created file
        """
        if filename is None:
            filename = self.generate_filename("results", "json")
        
        filepath = self.export_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=indent, ensure_ascii=False, default=str)
            
            self.logger.info(f"✅ Exported {len(results)} results to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export JSON: {e}")
            raise
    
    def export_csv(
        self,
        results: List[Dict[str, Any]],
        filename: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Path:
        """
        Export results to CSV file.
        
        Args:
            results: List of domain result dictionaries
            filename: Custom filename (optional, auto-generated if None)
            fields: List of fields to include (default: auto-detect from first result)
            
        Returns:
            Path to the created file
        """
        if not results:
            self.logger.warning("⚠️  No results to export")
            return None
        
        if filename is None:
            filename = self.generate_filename("results", "csv")
        
        filepath = self.export_dir / filename
        
        # Auto-detect fields from first result if not specified
        if fields is None:
            fields = self._extract_csv_fields(results[0])
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                
                for result in results:
                    # Flatten nested structures for CSV
                    flat_result = self._flatten_result(result)
                    writer.writerow(flat_result)
            
            self.logger.info(f"✅ Exported {len(results)} results to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export CSV: {e}")
            raise
    
    def _extract_csv_fields(self, result: Dict[str, Any]) -> List[str]:
        """
        Extract CSV field names from a result dictionary.
        Flattens nested structures with dot notation.
        
        Args:
            result: Sample result dictionary
            
        Returns:
            List of field names
        """
        fields = []
        
        # Basic fields
        if 'domain' in result:
            fields.append('domain')
        
        # Meta fields
        if 'meta' in result:
            meta = result['meta']
            for key in ['timestamp', 'status', 'execution_time_sec']:
                if key in meta:
                    fields.append(f'meta.{key}')
        
        # Check fields (flatten checks dict)
        if 'checks' in result:
            for check_name, check_data in result['checks'].items():
                if isinstance(check_data, dict):
                    # Add check status
                    fields.append(f'checks.{check_name}.status')
                    # Add specific check fields
                    if 'data' in check_data and isinstance(check_data['data'], dict):
                        for data_key in check_data['data'].keys():
                            fields.append(f'checks.{check_name}.data.{data_key}')
        
        return fields
    
    def _flatten_result(self, result: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary for CSV export.
        
        Args:
            result: Nested dictionary
            parent_key: Parent key for recursion
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        
        for key, value in result.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self._flatten_result(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                items.append((new_key, ', '.join(map(str, value))))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from results.
        
        Args:
            results: List of domain result dictionaries
            
        Returns:
            Summary statistics dictionary
        """
        if not results:
            return {
                'total_domains': 0,
                'successful': 0,
                'failed': 0,
                'error_rate': 0.0
            }
        
        total = len(results)
        successful = sum(1 for r in results if r.get('meta', {}).get('status') == 'success')
        failed = total - successful
        
        # Calculate average execution time
        exec_times = [
            r.get('meta', {}).get('execution_time_sec', 0) 
            for r in results 
            if r.get('meta', {}).get('execution_time_sec') is not None
        ]
        avg_exec_time = sum(exec_times) / len(exec_times) if exec_times else 0
        
        # Count check results
        check_stats = {}
        for result in results:
            for check_name, check_data in result.get('checks', {}).items():
                if check_name not in check_stats:
                    check_stats[check_name] = {'success': 0, 'error': 0}
                
                status = check_data.get('status', 'error')
                if status == 'success':
                    check_stats[check_name]['success'] += 1
                else:
                    check_stats[check_name]['error'] += 1
        
        return {
            'total_domains': total,
            'successful': successful,
            'failed': failed,
            'success_rate': round(successful / total * 100, 2) if total > 0 else 0,
            'error_rate': round(failed / total * 100, 2) if total > 0 else 0,
            'avg_execution_time_sec': round(avg_exec_time, 2),
            'check_statistics': check_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_summary(
        self,
        results: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Path:
        """
        Export summary statistics to JSON file.
        
        Args:
            results: List of domain result dictionaries
            filename: Custom filename (optional, auto-generated if None)
            
        Returns:
            Path to the created file
        """
        if filename is None:
            filename = self.generate_filename("summary", "json")
        
        filepath = self.export_dir / filename
        
        summary = self.generate_summary(results)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Summary exported to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export summary: {e}")
            raise
    
    def log_summary(self, results: List[Dict[str, Any]]) -> None:
        """
        Log summary statistics to console.
        
        Args:
            results: List of domain result dictionaries
        """
        summary = self.generate_summary(results)
        
        self.logger.info("=" * 60)
        self.logger.info("📊 SCAN SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Domains:     {summary['total_domains']}")
        self.logger.info(f"Successful:        {summary['successful']} ({summary['success_rate']}%)")
        self.logger.info(f"Failed:            {summary['failed']} ({summary['error_rate']}%)")
        self.logger.info(f"Avg Execution:     {summary['avg_execution_time_sec']}s")
        
        if summary['check_statistics']:
            self.logger.info("-" * 60)
            self.logger.info("Check Statistics:")
            for check_name, stats in summary['check_statistics'].items():
                success_pct = round(stats['success'] / (stats['success'] + stats['error']) * 100, 1)
                self.logger.info(f"  {check_name:20s} ✅ {stats['success']} ❌ {stats['error']} ({success_pct}%)")
        
        self.logger.info("=" * 60)


def export_results(
    results: List[Dict[str, Any]], 
    format: str = "json",
    export_dir: str = "exports",
    log_summary: bool = True,
    logger=None
) -> Optional[Path]:
    """
    Convenience function to export results.
    
    Args:
        results: List of domain result dictionaries
        format: Export format ('json' or 'csv')
        export_dir: Directory to store exports
        log_summary: Whether to log summary statistics
        logger: Custom logger instance (optional)
        
    Returns:
        Path to the created file
    """
    exporter = ResultExporter(export_dir, logger=logger)
    
    if log_summary:
        exporter.log_summary(results)
    
    if format.lower() == 'json':
        return exporter.export_json(results)
    elif format.lower() == 'csv':
        return exporter.export_csv(results)
    else:
        if logger:
            logger.error(f"❌ Unsupported format: {format}")
        return None
