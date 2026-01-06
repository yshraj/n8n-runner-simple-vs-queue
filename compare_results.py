#!/usr/bin/env python3
"""
Compare two webhook test result JSON files.
"""

import json
import sys
import os
from pathlib import Path


def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def compare_results(file1_path, file2_path):
    """Compare two test result files."""
    print("\n" + "="*60)
    print("Webhook Test Results Comparison")
    print("="*60)
    
    result1 = load_json(file1_path)
    result2 = load_json(file2_path)
    
    print(f"\nFile 1: {file1_path}")
    print(f"  URL: {result1.get('webhook_url', 'N/A')}")
    print(f"  Timestamp: {result1.get('test_timestamp', 'N/A')}")
    
    print(f"\nFile 2: {file2_path}")
    print(f"  URL: {result2.get('webhook_url', 'N/A')}")
    print(f"  Timestamp: {result2.get('test_timestamp', 'N/A')}")
    
    stats1 = result1.get('overall_statistics', {})
    stats2 = result2.get('overall_statistics', {})
    
    print("\n" + "="*60)
    print("OVERALL COMPARISON")
    print("="*60)
    
    # Total requests
    print(f"\nTotal Requests:")
    print(f"  File 1: {stats1.get('total_requests', 0)}")
    print(f"  File 2: {stats2.get('total_requests', 0)}")
    
    # Success rates
    success1 = stats1.get('overall_success_rate_percent', 0)
    success2 = stats2.get('overall_success_rate_percent', 0)
    print(f"\nSuccess Rate:")
    print(f"  File 1: {success1:.2f}%")
    print(f"  File 2: {success2:.2f}%")
    diff = success2 - success1
    print(f"  Difference: {diff:+.2f}% {'✅' if diff >= 0 else '❌'}")
    
    # Throughput
    rps1 = stats1.get('overall_requests_per_second', 0)
    rps2 = stats2.get('overall_requests_per_second', 0)
    print(f"\nThroughput (Requests/Second):")
    print(f"  File 1: {rps1:.2f} req/s")
    print(f"  File 2: {rps2:.2f} req/s")
    diff = rps2 - rps1
    print(f"  Difference: {diff:+.2f} req/s {'✅' if diff >= 0 else '❌'}")
    
    # Average duration
    avg1 = stats1.get('individual_request_statistics', {}).get('avg_duration_seconds', 0)
    avg2 = stats2.get('individual_request_statistics', {}).get('avg_duration_seconds', 0)
    print(f"\nAverage Request Duration:")
    print(f"  File 1: {avg1:.4f}s")
    print(f"  File 2: {avg2:.4f}s")
    diff = avg2 - avg1
    print(f"  Difference: {diff:+.4f}s {'✅' if diff <= 0 else '❌'}")
    
    # Min/Max
    min1 = stats1.get('individual_request_statistics', {}).get('min_duration_seconds', 0)
    max1 = stats1.get('individual_request_statistics', {}).get('max_duration_seconds', 0)
    min2 = stats2.get('individual_request_statistics', {}).get('min_duration_seconds', 0)
    max2 = stats2.get('individual_request_statistics', {}).get('max_duration_seconds', 0)
    
    print(f"\nMin Request Duration:")
    print(f"  File 1: {min1:.4f}s")
    print(f"  File 2: {min2:.4f}s")
    
    print(f"\nMax Request Duration:")
    print(f"  File 1: {max1:.4f}s")
    print(f"  File 2: {max2:.4f}s")
    
    # Batch-by-batch comparison
    print("\n" + "="*60)
    print("BATCH-BY-BATCH COMPARISON")
    print("="*60)
    
    batches1 = result1.get('test_batches', [])
    batches2 = result2.get('test_batches', [])
    
    for i, (batch1, batch2) in enumerate(zip(batches1, batches2), 1):
        size1 = batch1.get('batch_size', 0)
        size2 = batch2.get('batch_size', 0)
        
        if size1 != size2:
            continue
        
        print(f"\nBatch Size: {size1} requests")
        print(f"  File 1 - Total Time: {batch1.get('batch_total_duration_seconds', 0):.4f}s")
        print(f"  File 2 - Total Time: {batch2.get('batch_total_duration_seconds', 0):.4f}s")
        
        time1 = batch1.get('batch_total_duration_seconds', 0)
        time2 = batch2.get('batch_total_duration_seconds', 0)
        diff = time2 - time1
        print(f"  Difference: {diff:+.4f}s {'✅' if diff <= 0 else '❌'}")
        
        print(f"  File 1 - Avg Duration: {batch1.get('statistics', {}).get('avg_duration_seconds', 0):.4f}s")
        print(f"  File 2 - Avg Duration: {batch2.get('statistics', {}).get('avg_duration_seconds', 0):.4f}s")
    
    print("\n" + "="*60)


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_results.py <file1.json> <file2.json>")
        print("\nExample:")
        print("  python compare_results.py results/webhook_test_20250105_143000.json results/webhook_test_20250105_150000.json")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    # If relative paths, check in results folder
    if not os.path.isabs(file1) and not os.path.exists(file1):
        results_path = os.path.join("results", file1)
        if os.path.exists(results_path):
            file1 = results_path
    
    if not os.path.isabs(file2) and not os.path.exists(file2):
        results_path = os.path.join("results", file2)
        if os.path.exists(results_path):
            file2 = results_path
    
    compare_results(file1, file2)


if __name__ == "__main__":
    main()

