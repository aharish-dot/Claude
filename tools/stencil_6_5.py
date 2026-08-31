#!/usr/bin/env python3
"""Deprecated name. Forwards to tools/scj_stencil.py."""
import os, runpy
runpy.run_path(os.path.join(os.path.dirname(__file__), "scj_stencil.py"), run_name="__main__")
