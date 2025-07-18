#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

models = [
    'user',
    'property', 
    'lease',
    'payment',
    'maintenance',
    'message',
    'application',
    'document',
    'notification'
]

for model in models:
    try:
        print(f"Testing {model}...")
        exec(f"from src.models.{model} import *")
        print(f"✓ {model} imported successfully")
    except Exception as e:
        print(f"✗ {model} failed: {e}")
        import traceback
        traceback.print_exc()
        print()