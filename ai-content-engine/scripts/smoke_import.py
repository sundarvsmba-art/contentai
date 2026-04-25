"""Simple smoke-test: import key modules to catch syntax/import errors.

Run from repository root with:
    python ai-content-engine\scripts\smoke_import.py
"""
import sys
import importlib
import traceback

# Ensure package root is first on path
sys.path.insert(0, 'ai-content-engine')

modules = [
    'app.main',
    'app.core.config',
    'app.core.database',
    'app.services.ai.gemini_provider',
    'app.workers.celery_worker',
]

errors = False
for m in modules:
    try:
        importlib.import_module(m)
        print('Imported', m)
    except Exception:
        errors = True
        print('Failed to import', m)
        traceback.print_exc()

if errors:
    print('\nSmoke import test failed')
    sys.exit(1)

print('\nSmoke import test passed')
