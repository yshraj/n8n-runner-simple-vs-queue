#!/usr/bin/env python3
"""
Webhook Performance Test Script
Tests webhook URL with parallel requests and measures performance metrics.
"""

import asyncio
import aiohttp
import time
import json
import sys
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any


class WebhookTester:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.results = {
            "webhook_url": webhook_url,
            "test_timestamp": datetime.now().isoformat(),
            "test_batches": []
        }

    async def send_request(self, session: aiohttp.ClientSession, request_id: int) -> Dict[str, Any]:
        """Send a single request and measure its performance."""
        start_time = time.time()
        error = None
        status_code = None
        response_body = None
        
        # Generate unique session ID for each request
        session_id = str(uuid.uuid4()).replace('-', '')
        
        # Payload format for chat message webhook
        payload = [
            {
                "sessionId": session_id,
                "action": "sendMessage",
                "chatInput": "Hi"
            }
        ]
        
        try:
            async with session.post(
                self.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                status_code = response.status
                try:
                    response_body = await response.text()
                except:
                    response_body = None
                end_time = time.time()
                duration = end_time - start_time
        except asyncio.TimeoutError:
            end_time = time.time()
            duration = end_time - start_time
            error = "Timeout after 60 seconds"
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            error = str(e)
        
        return {
            "request_id": request_id,
            "session_id": session_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": round(duration, 4),
            "status_code": status_code,
            "error": error,
            "success": error is None and status_code in [200, 201, 202, 204],
            "response_body_preview": response_body[:200] if response_body else None
        }

    async def run_batch(self, batch_size: int) -> Dict[str, Any]:
        """Run a batch of parallel requests."""
        print(f"\n{'='*60}")
        print(f"Testing with {batch_size} parallel requests...")
        print(f"{'='*60}")
        
        batch_start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Create all tasks
            tasks = [
                self.send_request(session, i + 1)
                for i in range(batch_size)
            ]
            
            # Execute all requests in parallel
            results = await asyncio.gather(*tasks)
        
        batch_end_time = time.time()
        batch_total_duration = batch_end_time - batch_start_time
        
        # Calculate statistics
        durations = [r["duration_seconds"] for r in results]
        successful = sum(1 for r in results if r["success"])
        failed = batch_size - successful
        
        batch_result = {
            "batch_size": batch_size,
            "batch_start_time": batch_start_time,
            "batch_end_time": batch_end_time,
            "batch_total_duration_seconds": round(batch_total_duration, 4),
            "requests_per_second": round(batch_size / batch_total_duration, 2) if batch_total_duration > 0 else 0,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate_percent": round((successful / batch_size) * 100, 2) if batch_size > 0 else 0,
            "individual_requests": results,
            "statistics": {
                "min_duration_seconds": round(min(durations), 4) if durations else 0,
                "max_duration_seconds": round(max(durations), 4) if durations else 0,
                "avg_duration_seconds": round(sum(durations) / len(durations), 4) if durations else 0,
                "median_duration_seconds": round(sorted(durations)[len(durations) // 2], 4) if durations else 0
            }
        }
        
        # Print summary
        print(f"\nBatch Results:")
        print(f"  Total Time: {batch_total_duration:.4f} seconds")
        print(f"  Requests/Second: {batch_result['requests_per_second']:.2f}")
        print(f"  Successful: {successful}/{batch_size}")
        print(f"  Failed: {failed}/{batch_size}")
        print(f"  Success Rate: {batch_result['success_rate_percent']:.2f}%")
        
        # Show error details if all failed
        if failed == batch_size and results:
            first_error = results[0]
            if first_error.get('status_code') == 404:
                print(f"\n⚠️  All requests returned 404. Possible issues:")
                print(f"   - Webhook path '/chat' might not be configured in n8n")
                print(f"   - Workflow might not be active")
                print(f"   - Try URL without '/chat' path")
            elif first_error.get('error'):
                print(f"\n⚠️  Error: {first_error.get('error')}")
        
        print(f"\nIndividual Request Times:")
        print(f"  Min: {batch_result['statistics']['min_duration_seconds']:.4f}s")
        print(f"  Max: {batch_result['statistics']['max_duration_seconds']:.4f}s")
        print(f"  Avg: {batch_result['statistics']['avg_duration_seconds']:.4f}s")
        print(f"  Median: {batch_result['statistics']['median_duration_seconds']:.4f}s")
        
        return batch_result

    async def run_all_tests(self, batch_sizes: List[int] = [5, 10, 20]):
        """Run tests for all batch sizes."""
        print(f"\n{'#'*60}")
        print(f"# Webhook Performance Test")
        print(f"# URL: {self.webhook_url}")
        print(f"# Timestamp: {self.results['test_timestamp']}")
        print(f"{'#'*60}")
        
        for batch_size in batch_sizes:
            batch_result = await self.run_batch(batch_size)
            self.results["test_batches"].append(batch_result)
            
            # Small delay between batches to avoid overwhelming the server
            if batch_size != batch_sizes[-1]:  # Don't wait after last batch
                await asyncio.sleep(2)
        
        # Calculate overall statistics
        self._calculate_overall_stats()
        
        return self.results

    def _calculate_overall_stats(self):
        """Calculate overall statistics across all batches."""
        all_durations = []
        total_requests = 0
        total_successful = 0
        total_failed = 0
        total_time = 0
        
        for batch in self.results["test_batches"]:
            total_requests += batch["batch_size"]
            total_successful += batch["successful_requests"]
            total_failed += batch["failed_requests"]
            total_time += batch["batch_total_duration_seconds"]
            all_durations.extend([r["duration_seconds"] for r in batch["individual_requests"]])
        
        self.results["overall_statistics"] = {
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate_percent": round((total_successful / total_requests) * 100, 2) if total_requests > 0 else 0,
            "total_test_duration_seconds": round(total_time, 4),
            "overall_requests_per_second": round(total_requests / total_time, 2) if total_time > 0 else 0,
            "individual_request_statistics": {
                "min_duration_seconds": round(min(all_durations), 4) if all_durations else 0,
                "max_duration_seconds": round(max(all_durations), 4) if all_durations else 0,
                "avg_duration_seconds": round(sum(all_durations) / len(all_durations), 4) if all_durations else 0,
                "median_duration_seconds": round(sorted(all_durations)[len(all_durations) // 2], 4) if all_durations else 0
            }
        }

    def save_results(self, filename: str = None):
        """Save results to JSON file in results folder."""
        # Create results directory if it doesn't exist
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"webhook_test_{timestamp}.json"
        
        # Ensure filename ends with .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Full path to results file
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Results saved to: {filepath}")
        print(f"{'='*60}")
        return filepath

    def print_summary(self):
        """Print a summary of all test results."""
        if "overall_statistics" not in self.results:
            return
        
        stats = self.results["overall_statistics"]
        
        print(f"\n{'#'*60}")
        print(f"# OVERALL TEST SUMMARY")
        print(f"{'#'*60}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['total_successful']}")
        print(f"Failed: {stats['total_failed']}")
        print(f"Success Rate: {stats['overall_success_rate_percent']:.2f}%")
        print(f"Total Test Duration: {stats['total_test_duration_seconds']:.4f} seconds")
        print(f"Overall Throughput: {stats['overall_requests_per_second']:.2f} requests/second")
        print(f"\nIndividual Request Performance:")
        print(f"  Min: {stats['individual_request_statistics']['min_duration_seconds']:.4f}s")
        print(f"  Max: {stats['individual_request_statistics']['max_duration_seconds']:.4f}s")
        print(f"  Avg: {stats['individual_request_statistics']['avg_duration_seconds']:.4f}s")
        print(f"  Median: {stats['individual_request_statistics']['median_duration_seconds']:.4f}s")
        print(f"{'#'*60}")


async def main():
    """Interactive main function that asks for webhook URL."""
    print("\n" + "="*60)
    print("Webhook Performance Test Tool")
    print("="*60)
    print("\nThis script will test your webhook with parallel requests.")
    print("It will send requests in batches: 5, 10, and 20 requests.")
    print("\nPayload format:")
    print(json.dumps([{
        "sessionId": "<unique-id>",
        "action": "sendMessage",
        "chatInput": "Hi"
    }], indent=2))
    print("\n" + "-"*60)
    
    # Ask for webhook URL
    while True:
        webhook_url = input("\nPlease paste your webhook URL: ").strip()
        
        if not webhook_url:
            print("Error: URL cannot be empty. Please try again.")
            continue
        
        if not webhook_url.startswith(('http://', 'https://')):
            print("Error: URL must start with http:// or https://")
            print("Example: http://localhost:5678/webhook/abc123")
            continue
        
        # Check if URL has /chat path and suggest testing
        if '/chat' in webhook_url:
            print(f"\n⚠️  Note: URL contains '/chat' path")
            print(f"   If you get 404 errors, try the base URL without '/chat'")
            print(f"   Base URL would be: {webhook_url.rsplit('/chat', 1)[0]}")
        
        # Confirm URL
        print(f"\nWebhook URL: {webhook_url}")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        if confirm in ['y', 'yes', '']:
            break
        else:
            print("Please enter the URL again.")
    
    # Default batch sizes
    batch_sizes = [5, 10, 20]
    
    print(f"\n{'='*60}")
    print("Starting performance test...")
    print(f"Batch sizes: {batch_sizes}")
    print(f"{'='*60}")
    
    # Create tester and run tests
    tester = WebhookTester(webhook_url)
    
    try:
        results = await tester.run_all_tests(batch_sizes)
        tester.print_summary()
        output_file = tester.save_results()
        
        print(f"\n✅ Test completed successfully!")
        print(f"📁 Results saved to: {output_file}")
        print(f"\n💡 Tip: You can compare this run with previous runs by comparing JSON files in the 'results' folder.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

