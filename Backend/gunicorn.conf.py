import os

# Gunicorn configuration for Render deployment
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = 1
threads = 4
timeout = 300  # 5 minutes timeout to allow deep chunking of multi-page PDFs
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
