"""Dashboard.

This project starts a Plotly Dash Flask server to visualise data on disk
"""

# Standard Library
import argparse
import sys

from .dashboard import dashboard


def _parse_cli_args(args):
    parser = argparse.ArgumentParser(description="Dashboard server configuration")
    parser.add_argument("path", type=str, default=".", help="The path to the root data directory")
    return parser.parse_args(args[1:])


if __name__ == "__main__":
    dashboard(_parse_cli_args(sys.argv).path).run_server(debug=True)
