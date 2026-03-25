#!/usr/bin/env python3
"""Exercise #1: Upload three text files to S3 using boto3."""

import argparse
import logging
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


def upload_files(bucket_name: str, files: list[str], prefix: str = "") -> None:
    s3 = boto3.client("s3")
    start_time = time.time()
    print(f"Upload start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    for file_name in files:
        file_path = Path(file_name)
        if not file_path.exists():
            logging.error("File not found: %s", file_path)
            continue

        s3_key = f"{prefix}{file_path.name}" if prefix else file_path.name
        print(f"Starting upload: {file_path.name}")
        try:
            s3.upload_file(str(file_path), bucket_name, s3_key)
            print(f"Uploaded: {file_path.name} -> s3://{bucket_name}/{s3_key}")
        except ClientError:
            logging.exception("Failed to upload %s to bucket %s", file_path.name, bucket_name)

    end_time = time.time()
    print(f"Upload end time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Total upload duration: {end_time - start_time:.2f} seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload assignment text files to an S3 bucket."
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="Target S3 bucket name.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional S3 key prefix (example: assignment1/).",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=["izzet1.txt", "izzet2.txt", "izzet3.txt"],
        help="Files to upload (defaults to izzet1.txt izzet2.txt izzet3.txt).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    upload_files(args.bucket, args.files, args.prefix)
