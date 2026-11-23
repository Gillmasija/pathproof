"""Command entry point."""
import argparse

from . import __version__


def main():
    parser = argparse.ArgumentParser(description="Offline static HTML link checker")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
