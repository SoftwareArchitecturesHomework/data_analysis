# main.py (FastAPI setup)
import os
import sys

from config.settings import settings


MSYS2_DLL_PATH = settings.msys2_dll_path

if os.path.exists(MSYS2_DLL_PATH):
    # Option A (Standard Python Path Injection): Add the directory to os.environ['PATH']
    # This is necessary because the Windows DLL loader searches this variable.
    os.environ['PATH'] = MSYS2_DLL_PATH + os.pathsep + os.environ['PATH']

    # Option B (Python 3.8+): Use add_dll_directory for explicit search (optional, but safe)
    if sys.version_info >= (3, 8):
        os.add_dll_directory(MSYS2_DLL_PATH)

    print(f"✅ Injected GTK+ DLL path: {MSYS2_DLL_PATH}")
else:
    print(f"❌ FATAL: MSYS2 DLL path not found at {MSYS2_DLL_PATH}. Cannot run WeasyPrint.")
    sys.exit(1)

from server.rest_router import router

import uvicorn
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.grpc_host, port=settings.grpc_port, reload=True)