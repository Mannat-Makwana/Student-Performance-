#!/usr/bin/env python
"""Run Django management commands for the project."""

import os
import sys


def main():
    """Execute a Django management command."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

