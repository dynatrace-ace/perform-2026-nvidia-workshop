#!/usr/bin/env python3
"""
Update NeMo Guardrails and NAT configuration files.

This script manages configuration files for different deployment environments (local, build, brev).
It performs two main operations:
1. Copies environment-specific template config files (config.yml.local, config.yml.build, 
   config.yml.brev) to the active config.yml files
2. For 'brev' deployments, replaces placeholder values with actual NVIDIA model endpoint URLs
   from environment variables

Usage:
    python update_config.py local   # Copies config.yml.local → config.yml
    python update_config.py build   # Copies config.yml.build → config.yml
    python update_config.py brev    # Copies config.yml.brev → config.yml and replaces placeholders

Environment Variables (required for 'brev' config type):
    - NVIDIA_MODEL_ENDPOINT_8001: Main LLM endpoint URL
    - NVIDIA_MODEL_ENDPOINT_8002: Content safety model endpoint URL
    - NVIDIA_MODEL_ENDPOINT_8003: Topic control model endpoint URL
    - NVIDIA_MODEL_ENDPOINT_8004: Additional model endpoint URL

Config File Locations:
    - guardrails_config/config.yml
    - src/nat_simple_web_query/configs/config.yml
"""

import argparse
import os
import shutil
from pathlib import Path

def copy_config_template(config_type):
    """Copy config template files to active config.yml based on config type."""
    # Determine config file suffix based on config type
    if config_type == "local":
        suffix = ".local"
    elif config_type == "build":
        suffix = ".build"
    elif config_type == "brev":
        suffix = ".brev"
    else:
        print(f"❌ Error: Invalid config type: {config_type}. Must be 'local', 'build', or 'brev'")
        exit(1)
    
    # Define config directories
    guardrails_dir = Path("guardrails_config")
    nat_dir = Path("src/nat_simple_web_query/configs")
    
    # Copy template files to config.yml
    for config_dir in [guardrails_dir, nat_dir]:
        source_file = config_dir / f"config.yml{suffix}"
        dest_file = config_dir / "config.yml"
        
        if not source_file.exists():
            print(f"❌ Error: {source_file} not found")
            exit(1)
        
        shutil.copy2(source_file, dest_file)
        print(f"✓ Copied {source_file} → {dest_file}")

def update_brev_endpoint(config_type):

    # Construct config file paths
    guardrails_config_path = Path(f"guardrails_config/config.yml")
    nat_config_path = Path(f"src/nat_simple_web_query/configs/config.yml")
    
    # Check if all required environment variables are set
    required_vars = ["NVIDIA_MODEL_ENDPOINT_8001","NVIDIA_MODEL_ENDPOINT_8002", 
                     "NVIDIA_MODEL_ENDPOINT_8003", "NVIDIA_MODEL_ENDPOINT_8004"]
    missing_vars = [var for var in required_vars if not os.environ.get(var, "").strip()]
    
    if missing_vars:
        print(f"❌ Error: The following environment variables are not set or empty: {', '.join(missing_vars)}")
        exit(1)
    
    # Get endpoints from environment variables
    endpoint_8001 = os.environ.get("NVIDIA_MODEL_ENDPOINT_8001")
    endpoint_8002 = os.environ.get("NVIDIA_MODEL_ENDPOINT_8002")
    endpoint_8003 = os.environ.get("NVIDIA_MODEL_ENDPOINT_8003")
    endpoint_8004 = os.environ.get("NVIDIA_MODEL_ENDPOINT_8004")
    
    # Process both config files
    for config_path in [guardrails_config_path, nat_config_path]:
        if not config_path.exists():
            print(f"❌ Error: {config_path} not found")
            exit(1)
            
        # Read the file
        content = config_path.read_text()
        
        # Replace all placeholders
        updated_content = content.replace(
            "NVIDIA_MODEL_ENDPOINT_8001_PLACEHOLDER",
            endpoint_8001
        )
        updated_content = updated_content.replace(
            "NVIDIA_MODEL_ENDPOINT_8002_PLACEHOLDER",
            endpoint_8002
        )
        updated_content = updated_content.replace(
            "NVIDIA_MODEL_ENDPOINT_8003_PLACEHOLDER",
            endpoint_8003
        )
        updated_content = updated_content.replace(
            "NVIDIA_MODEL_ENDPOINT_8004_PLACEHOLDER",
            endpoint_8004
        )
        
        # Write back to file
        config_path.write_text(updated_content)
        print(f"✓ Updated {config_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update endpoint URLs in config files")
    parser.add_argument(
        "config_type",
        choices=["local", "build", "brev"],
        help="Config type: 'local' for .local files, 'build' for .build files, 'brev' for default config.yml"
    )
    
    args = parser.parse_args()
    print(f"Updating config files for config type: {args.config_type}")
    
    # First copy the template files
    copy_config_template(args.config_type)
    
    # Then update the endpoints (only for brev config type)
    if args.config_type == "brev":
        update_brev_endpoint(args.config_type)
