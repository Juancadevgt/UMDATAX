import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import router
from backend.app.routes_pbi import router_pbi

# Instalar Chromium al iniciar
subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
subprocess.run([sys.executable, "-m", "playwright", "install-deps", "chromium"], check=False)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_pbi)