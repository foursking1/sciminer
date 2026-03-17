#!/usr/bin/env python
"""
PDF Parser using MinerU - Extract text and structure from PDF documents
Usage: python parse_pdf.py <input.pdf> [output_dir]
"""

import os
import sys
import json
import hashlib
from datetime import datetime

# Disable PaddleOCR model source check
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

# ============================================================================
# PATCH: Must be applied BEFORE importing any magic_pdf modules
# PaddleOCR 3.x renamed PPStructure to PPStructureV3
# ============================================================================
import paddleocr
if not hasattr(paddleocr, 'PPStructure'):
    paddleocr.PPStructure = paddleocr.PPStructureV3
    print("[Patch] PPStructure -> PPStructureV3")

# Now we can safely import MinerU
import magic_pdf.model as model_config
model_config.__use_inside_model__ = True
print("[Config] Enabled inside model")

from magic_pdf.pipe.TXTPipe import TXTPipe
from magic_pdf.pipe.OCRPipe import OCRPipe
from magic_pdf.pipe.AbsPipe import AbsPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter


def compute_file_hash(pdf_path: str) -> str:
    """Compute MD5 hash of file for cache invalidation."""
    with open(pdf_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def generate_metadata(pdf_path: str, method: str, output_dir: str, char_count: int, file_hash: str) -> dict:
    """Generate metadata for parsed document."""
    return {
        "source_file": os.path.basename(pdf_path),
        "source_hash": file_hash,
        "parse_method": method,
        "parse_time": datetime.now().isoformat(),
        "output_char_count": char_count,
        "output_dir": output_dir,
        "status": "completed"
    }


def is_already_parsed(pdf_path: str, output_dir: str, force: bool = False, file_hash: str = None) -> bool:
    """Check if document is already parsed and cache is valid."""
    if force:
        return False

    metadata_path = os.path.join(output_dir, "metadata.json")
    output_path = os.path.join(output_dir, "output_mineru.md")

    if not os.path.exists(metadata_path) or not os.path.exists(output_path):
        return False

    # Check if source file changed
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        current_hash = file_hash if file_hash else compute_file_hash(pdf_path)
        return metadata.get("source_hash") == current_hash
    except (IOError, json.JSONDecodeError, KeyError):
        return False


def parse_pdf(pdf_path: str, output_dir: str = None, method: str = "auto", force: bool = False) -> str:
    """
    Parse PDF using MinerU and return markdown content.

    Args:
        pdf_path: Path to input PDF file
        output_dir: Output directory (default: parsed_documents/<doc_name>)
        method: Parse method - "auto", "txt", or "ocr"
        force: Force re-parse even if cached version exists

    Returns:
        Markdown content string
    """
    # Derive document name from filename
    doc_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Default output directory
    if output_dir is None:
        # Find project root (where parsed_documents should be)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
        output_dir = os.path.join(project_root, "parsed_documents", doc_name)

    os.makedirs(output_dir, exist_ok=True)

    # Compute file hash once for cache check and metadata
    file_hash = compute_file_hash(pdf_path)

    # Check cache
    if is_already_parsed(pdf_path, output_dir, force, file_hash):
        print(f"[MinerU] Cache hit: {doc_name} already parsed")
        output_file = os.path.join(output_dir, "output_mineru.md")
        with open(output_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Read PDF
    print(f"[MinerU] Reading {pdf_path}...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Create image writer
    image_dir = os.path.join(output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    disk_rw = DiskReaderWriter(image_dir)

    # Determine PDF type
    if method == "auto":
        pdf_type = AbsPipe.classify(pdf_bytes)
        print(f"[MinerU] Auto-detected PDF type: {pdf_type}")
    else:
        pdf_type = method
        print(f"[MinerU] Using specified PDF type: {pdf_type}")

    # Use appropriate pipe based on PDF type
    print(f"[MinerU] Initializing model and parsing...")
    if pdf_type == "txt":
        pipe = TXTPipe(pdf_bytes, [], disk_rw, is_debug=True)
    else:
        pipe = OCRPipe(pdf_bytes, [], disk_rw, is_debug=True)

    # Analyze (runs PaddleOCR model to generate layout detection)
    print("[MinerU] Running layout analysis...")
    pipe.pipe_analyze()

    # Parse
    print("[MinerU] Parsing...")
    pipe.pipe_parse()
    print("[MinerU] Parsing completed")

    # Get markdown using the correct API
    img_bucket_path = os.path.basename(image_dir)
    md_content = pipe.pipe_mk_markdown(img_bucket_path)

    # Save output
    output_file = os.path.join(output_dir, "output_mineru.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[MinerU] Output saved to {output_file}")
    print(f"[MinerU] Total characters: {len(md_content)}")

    # Save metadata
    metadata = generate_metadata(pdf_path, method, output_dir, len(md_content), file_hash)
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"[MinerU] Metadata saved to {metadata_path}")

    return md_content


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse PDF with MinerU")
    parser.add_argument("input_pdf", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output directory", default=None)
    parser.add_argument("-m", "--method", choices=["auto", "txt", "ocr"], default="auto",
                        help="Parse method: auto (default), txt (text PDF), ocr (scanned PDF)")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force re-parse even if cached version exists")
    args = parser.parse_args()

    if not os.path.exists(args.input_pdf):
        print(f"Error: File not found: {args.input_pdf}")
        sys.exit(1)

    parse_pdf(args.input_pdf, args.output, args.method, args.force)


if __name__ == "__main__":
    main()
