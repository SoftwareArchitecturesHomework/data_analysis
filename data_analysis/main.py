# main.py (FastAPI setup)
import os
import sys
import platform

from config.settings import settings


MSYS2_DLL_PATH = settings.msys2_dll_path

# Only apply Windows-specific DLL path handling
if platform.system() == 'Windows' and os.path.exists(MSYS2_DLL_PATH):
    # Option A (Standard Python Path Injection): Add the directory to os.environ['PATH']
    # This is necessary because the Windows DLL loader searches this variable.
    os.environ['PATH'] = MSYS2_DLL_PATH + os.pathsep + os.environ['PATH']

    # Option B (Python 3.8+): Use add_dll_directory for explicit search (optional, but safe)
    if sys.version_info >= (3, 8) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(MSYS2_DLL_PATH)

    print(f"✅ Injected GTK+ DLL path: {MSYS2_DLL_PATH}")
elif platform.system() == 'Windows':
    print(f"⚠️  WARNING: MSYS2 DLL path not found at {MSYS2_DLL_PATH}. WeasyPrint may not work on Windows.")
else:
    print(f"✅ Running on {platform.system()}, GTK libraries expected from system packages")

from server.rest_router import router

import uvicorn
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    # Use import string for reload to work, or disable reload in production
    uvicorn.run("main:app", host=settings.grpc_host, port=settings.grpc_port, reload=False)