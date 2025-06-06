#!/usr/bin/env python3
import argparse
import asyncio
import io
import json
import os
import random
import statistics
import time
from datetime import datetime
from pathlib import Path

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

# Configuration
DEFAULT_API_URL = "http://localhost:8080"
DEFAULT_OUTPUT_DIR = "upload_test_results"
SAMPLE_DOCUMENTS_DIR = "test_documents"


class DocumentUploadTester:
    def __init__(
        self,
        api_url=DEFAULT_API_URL,
        output_dir=DEFAULT_OUTPUT_DIR,
        documents_dir=SAMPLE_DOCUMENTS_DIR,
    ):
        self.api_url = api_url
        self.output_dir = output_dir
        self.documents_dir = documents_dir
        self.results = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Ensure test documents directory exists
        os.makedirs(documents_dir, exist_ok=True)

    def get_test_files(self, file_type=None, max_files=None):
        """Get list of test files, optionally filtered by type"""
        files = []

        path = Path(self.documents_dir)

        if file_type:
            # Filter by file extension
            files = list(path.glob(f"*.{file_type}"))
        else:
            # Get all supported file types
            for ext in ["pdf", "txt", "docx", "md"]:
                files.extend(list(path.glob(f"*.{ext}")))

        # If max_files is specified, limit the number of files
        if max_files and len(files) > max_files:
            return random.sample(files, max_files)

        return files

    def generate_test_files(self, num_files=5, file_types=None, sizes=None):
        """Generate test files with varying sizes and content"""
        if not file_types:
            file_types = ["txt", "md"]

        if not sizes:
            # Create files of different sizes (in KB)
            sizes = [5, 20, 100, 500, 1000]

        created_files = []

        for i in range(min(num_files, len(sizes))):
            # Select file type and size
            file_type = random.choice(file_types)
            size_kb = sizes[i % len(sizes)]

            # Create a unique filename
            timestamp = int(time.time())
            filename = f"test_doc_{timestamp}_{i}_{size_kb}KB.{file_type}"
            filepath = os.path.join(self.documents_dir, filename)

            # Generate content
            content_lines = []
            line_template = "This is line {line_num} of the test document {doc_id}. It contains test content for performance testing.\n"

            # Calculate number of lines needed for target size
            bytes_per_line = len(line_template.format(line_num=1, doc_id=i))
            num_lines = (size_kb * 1024) // bytes_per_line

            # Generate the content
            for line_num in range(1, num_lines + 1):
                content_lines.append(line_template.format(line_num=line_num, doc_id=i))

            # Write to file
            with open(filepath, "w") as f:
                f.writelines(content_lines)

            created_files.append(filepath)
            print(f"Created test file: {filepath} ({size_kb} KB)")

        return created_files

    async def upload_files(
        self, files, prompt="Summarize the key points in these documents", models=None
    ):
        """Upload files to the Ultra Framework and process them"""
        if not models:
            models = ["claude", "chatgpt"]

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                # Prepare the form data
                data = aiohttp.FormData()
                data.add_field("prompt", prompt)
                data.add_field("selectedModels", json.dumps(models))
                data.add_field("ultraModel", models[0])
                data.add_field("pattern", "Confidence Analysis")
                data.add_field("options", "{}")

                # Add files to form data
                for file_path in files:
                    file_name = os.path.basename(file_path)
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        data.add_field(
                            "files",
                            io.BytesIO(file_content),
                            filename=file_name,
                            content_type=self.get_content_type(file_path),
                        )

                # Make the API request
                async with session.post(
                    f"{self.api_url}/api/analyze-with-docs", data=data
                ) as response:
                    status_code = response.status

                    if status_code == 200:
                        response_data = await response.json()
                    else:
                        error_text = await response.text()
                        print(f"Error: {status_code}, {error_text}")
                        response_data = {"error": error_text}

        except Exception as e:
            print(f"Exception during file upload: {str(e)}")
            status_code = 500
            response_data = {"error": str(e)}

        end_time = time.time()
        duration = end_time - start_time

        # Calculate file sizes
        total_size_bytes = sum(os.path.getsize(file) for file in files)
        total_size_mb = total_size_bytes / (1024 * 1024)

        # Create result record
        result = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "status_code": status_code,
            "files_count": len(files),
            "total_size_mb": total_size_mb,
            "prompt_length": len(prompt),
            "prompt": prompt,
            "models": models,
            "success": status_code == 200,
            "files": [str(f) for f in files],
        }

        # Extract processing details if available
        if status_code == 200 and "document_metadata" in response_data:
            result["chunks_used"] = response_data["document_metadata"].get(
                "chunks_used", 0
            )
            result["processing_time"] = response_data.get("processing_time", 0)

        self.results.append(result)
        return result

    def get_content_type(self, file_path):
        """Determine the content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()

        content_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".md": "text/markdown",
        }

        return content_types.get(ext, "application/octet-stream")

    async def run_upload_test(self, test_config):
        """Run an upload test with the specified configuration"""
        print(f"Running document upload test with configuration:")
        for key, value in test_config.items():
            print(f"  {key}: {value}")

        # Get or generate test files
        if test_config.get("generate_files", False):
            files = self.generate_test_files(
                num_files=test_config.get("num_files", 3),
                file_types=test_config.get("file_types", ["txt", "md"]),
                sizes=test_config.get("file_sizes", [5, 50, 200]),  # KB
            )
        else:
            files = self.get_test_files(
                file_type=test_config.get("file_type"),
                max_files=test_config.get("max_files"),
            )

        if not files:
            print(
                f"No test files found in {self.documents_dir}. Please add test files or use --generate option."
            )
            return None

        # Use specified or default prompt
        prompt = test_config.get(
            "prompt", "Summarize the key points from these documents"
        )

        # Use specified or default models
        models = test_config.get("models", ["claude", "chatgpt"])

        print(
            f"Uploading {len(files)} files, total size: {sum(os.path.getsize(f) for f in files) / (1024*1024):.2f} MB"
        )
        result = await self.upload_files(files, prompt, models)

        print(f"\nTest completed in {result['duration_seconds']:.2f} seconds")
        print(f"Status: {'Successful' if result['success'] else 'Failed'}")

        if result["success"]:
            print(f"Chunks used: {result.get('chunks_used', 'N/A')}")
            print(
                f"Backend processing time: {result.get('processing_time', 'N/A'):.2f} seconds"
            )

        return result

    async def run_batch_test(self, test_configs):
        """Run a batch of upload tests with different configurations"""
        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = f"{self.output_dir}/batch_test_{timestamp}"
        os.makedirs(batch_dir, exist_ok=True)

        print(f"Running batch test with {len(test_configs)} configurations")

        for i, config in enumerate(test_configs):
            print(f"\nTest {i+1}/{len(test_configs)}")
            result = await self.run_upload_test(config)
            if result:
                results.append(result)

        # Save results
        if results:
            results_df = pd.DataFrame(results)
            results_df.to_csv(f"{batch_dir}/batch_results.csv", index=False)

            with open(f"{batch_dir}/batch_results.json", "w") as f:
                json.dump(results, f, indent=2)

            # Generate visualizations
            self.generate_batch_visualizations(results, batch_dir)

        return results

    async def run_size_scaling_test(
        self, file_sizes=None, prompt="Analyze the content of these documents"
    ):
        """Test scaling of processing time with document size"""
        if not file_sizes:
            # Size in KB
            file_sizes = [10, 50, 100, 250, 500, 1000]

        test_configs = []

        # Create a config for each file size
        for size in file_sizes:
            test_configs.append(
                {
                    "generate_files": True,
                    "num_files": 1,
                    "file_types": ["txt"],
                    "file_sizes": [size],
                    "prompt": prompt,
                    "models": ["claude", "chatgpt"],
                    "test_name": f"Size_Test_{size}KB",
                }
            )

        return await self.run_batch_test(test_configs)

    async def run_count_scaling_test(self, file_counts=None, file_size_kb=100):
        """Test scaling of processing time with number of documents"""
        if not file_counts:
            file_counts = [1, 2, 3, 5, 8, 10]

        test_configs = []

        # Create a config for each file count
        for count in file_counts:
            test_configs.append(
                {
                    "generate_files": True,
                    "num_files": count,
                    "file_types": ["txt"],
                    "file_sizes": [file_size_kb] * count,  # Same size for all files
                    "prompt": f"Analyze and summarize these {count} documents",
                    "models": ["claude", "chatgpt"],
                    "test_name": f"Count_Test_{count}_Files",
                }
            )

        return await self.run_batch_test(test_configs)

    def generate_batch_visualizations(self, results, output_dir):
        """Generate visualizations for batch test results"""
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)

        # Process times vs. file size
        plt.figure(figsize=(10, 6))
        plt.scatter(df["total_size_mb"], df["duration_seconds"], alpha=0.7)

        # Add trendline
        if len(df) > 1:
            z = np.polyfit(df["total_size_mb"], df["duration_seconds"], 1)
            p = np.poly1d(z)
            plt.plot(df["total_size_mb"], p(df["total_size_mb"]), "r--")

        plt.title("Processing Time vs. File Size")
        plt.xlabel("Total File Size (MB)")
        plt.ylabel("Processing Time (seconds)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.savefig(f"{output_dir}/time_vs_size.png")

        # Process times vs. file count
        plt.figure(figsize=(10, 6))
        plt.scatter(df["files_count"], df["duration_seconds"], alpha=0.7)

        # Add trendline
        if len(df) > 1:
            z = np.polyfit(df["files_count"], df["duration_seconds"], 1)
            p = np.poly1d(z)
            plt.plot(df["files_count"], p(df["files_count"]), "r--")

        plt.title("Processing Time vs. Number of Files")
        plt.xlabel("Number of Files")
        plt.ylabel("Processing Time (seconds)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.savefig(f"{output_dir}/time_vs_count.png")

        # If we have chunks_used data
        if "chunks_used" in df and not df["chunks_used"].isna().all():
            plt.figure(figsize=(10, 6))
            plt.scatter(df["chunks_used"], df["duration_seconds"], alpha=0.7)

            # Add trendline
            if len(df) > 1:
                z = np.polyfit(df["chunks_used"], df["duration_seconds"], 1)
                p = np.poly1d(z)
                plt.plot(df["chunks_used"], p(df["chunks_used"]), "r--")

            plt.title("Processing Time vs. Chunks Used")
            plt.xlabel("Chunks Used")
            plt.ylabel("Processing Time (seconds)")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.savefig(f"{output_dir}/time_vs_chunks.png")

        plt.close("all")

    def save_results(self):
        """Save all test results to output directory"""
        if not self.results:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save as CSV
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(
            f"{self.output_dir}/upload_results_{timestamp}.csv", index=False
        )

        # Save as JSON
        with open(f"{self.output_dir}/upload_results_{timestamp}.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to {self.output_dir}")


async def main():
    parser = argparse.ArgumentParser(
        description="Ultra Framework Document Upload Tester"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_API_URL,
        help=f"API base URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for test results (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=SAMPLE_DOCUMENTS_DIR,
        help=f"Directory containing test documents (default: {SAMPLE_DOCUMENTS_DIR})",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "batch", "size-scaling", "count-scaling"],
        default="single",
        help="Test mode",
    )

    # Single test parameters
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate test files instead of using existing ones",
    )
    parser.add_argument(
        "--num-files",
        type=int,
        default=3,
        help="Number of files to use/generate for the test",
    )
    parser.add_argument(
        "--file-type",
        type=str,
        choices=["pdf", "txt", "docx", "md"],
        help="File type to use (for existing files)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Summarize the key points from these documents",
        help="Prompt to use for document analysis",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="claude,chatgpt",
        help="Comma-separated list of models to use",
    )

    args = parser.parse_args()

    # Initialize tester
    tester = DocumentUploadTester(args.url, args.output, args.docs_dir)

    # Parse models
    models = args.models.split(",")

    if args.mode == "single":
        # Run a single test
        await tester.run_upload_test(
            {
                "generate_files": args.generate,
                "num_files": args.num_files,
                "file_type": args.file_type,
                "max_files": args.num_files,
                "prompt": args.prompt,
                "models": models,
            }
        )

    elif args.mode == "batch":
        # Run a batch test with different configurations
        test_configs = [
            # Small file test
            {
                "generate_files": True,
                "num_files": 3,
                "file_types": ["txt"],
                "file_sizes": [10, 20, 30],  # KB
                "prompt": "Summarize these small documents",
                "models": ["claude", "chatgpt"],
                "test_name": "Small_Files_Test",
            },
            # Medium file test
            {
                "generate_files": True,
                "num_files": 2,
                "file_types": ["txt", "md"],
                "file_sizes": [200, 300],  # KB
                "prompt": "Analyze these medium-sized documents",
                "models": ["claude", "chatgpt"],
                "test_name": "Medium_Files_Test",
            },
            # Large file test
            {
                "generate_files": True,
                "num_files": 1,
                "file_types": ["txt"],
                "file_sizes": [1000],  # 1MB
                "prompt": "Provide a detailed analysis of this large document",
                "models": ["claude", "chatgpt"],
                "test_name": "Large_File_Test",
            },
            # Multiple small files test
            {
                "generate_files": True,
                "num_files": 8,
                "file_types": ["txt"],
                "file_sizes": [50] * 8,  # 8 files of 50KB each
                "prompt": "Identify common themes across these documents",
                "models": ["claude", "chatgpt"],
                "test_name": "Multiple_Files_Test",
            },
        ]

        await tester.run_batch_test(test_configs)

    elif args.mode == "size-scaling":
        # Run size scaling test
        await tester.run_size_scaling_test()

    elif args.mode == "count-scaling":
        # Run count scaling test
        await tester.run_count_scaling_test()

    # Save results
    tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())
