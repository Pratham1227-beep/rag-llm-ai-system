# api/index.py
import os
import sys

# Add Backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from app import create_app

app = create_app()
