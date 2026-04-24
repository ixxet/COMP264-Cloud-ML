"""
SafeView backend support package.

Chalice loads modules from chalicelib at deploy/runtime. The package is kept
small and explicit: app.py owns HTTP routing, while sibling modules own image
validation, S3 persistence, AWS AI orchestration, and report assembly.
"""
