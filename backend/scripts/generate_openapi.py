#!/usr/bin/env python
"""Generate OpenAPI specification from FastAPI application.

This script generates the OpenAPI spec and writes it to the contracts directory.

Usage:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --output path/to/openapi.yaml
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def generate_openapi_spec() -> dict:
    """Generate OpenAPI specification from the FastAPI app."""
    # Add src to path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    from src.main import create_app

    app = create_app()
    return app.openapi()


def save_spec(spec: dict, output_path: Path, format: str = "yaml") -> None:
    """Save the OpenAPI spec to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        if format == "yaml":
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        else:
            json.dump(spec, f, indent=2)

    print(f"OpenAPI spec saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI specification")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(__file__).parent.parent.parent / "specs" / "003-perpetua-backend" / "contracts" / "openapi-generated.yaml",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (yaml or json)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of file",
    )

    args = parser.parse_args()

    try:
        spec = generate_openapi_spec()

        if args.stdout:
            if args.format == "yaml":
                print(yaml.dump(spec, default_flow_style=False, allow_unicode=True))
            else:
                print(json.dumps(spec, indent=2))
        else:
            save_spec(spec, args.output, args.format)

        print(f"OpenAPI spec generated successfully!")
        print(f"  Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"  Version: {spec.get('info', {}).get('version', 'Unknown')}")
        print(f"  Paths: {len(spec.get('paths', {}))}")

    except Exception as e:
        print(f"Error generating OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
