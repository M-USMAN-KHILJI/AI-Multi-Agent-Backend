import sys
import os
from fastapi import FastAPI, Request

# Add root directory to sys.path so 'app' imports work seamlessly on Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app as base_app

# Wrapper to strip /api/index prefix if injected by Vercel rewrite
class StripPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/index"):
                # Strip the /api/index prefix
                new_path = path[len("/api/index"):] or "/"
                scope["path"] = new_path
                scope["raw_path"] = new_path.encode("ascii")
        await self.app(scope, receive, send)

app = StripPrefixMiddleware(base_app)

