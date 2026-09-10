"""KR FrontWatch single-service product shell around frozen Laptop replay authority."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from .frozen_replay import ROOT, VERSION, STATE, router, load_authority
from .model_bridge import replay_code, status as model_replay_status

@asynccontextmanager
async def lifespan(app):
    STATE.update(load_authority())
    yield
    STATE.clear()

app=FastAPI(title="KR FrontWatch AI",version=VERSION,lifespan=lifespan,
            docs_url=None,redoc_url=None,openapi_url=None)
app.add_middleware(GZipMiddleware,minimum_size=1024)
app.mount("/static",StaticFiles(directory=ROOT/"static"),name="static")
app.include_router(router)

@app.middleware("http")
async def security_headers(request,call_next):
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="no-referrer"
    response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"]=(
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; "
        "frame-ancestors 'none'; form-action 'self'")
    response.headers["Cache-Control"]="no-store" if request.url.path.startswith("/api/") else "no-cache"
    return response

@app.get("/healthz")
def health():
    if not STATE.get("ready"):
        raise HTTPException(503,"Frozen authority not ready")
    return {"status":"ok","app_version":VERSION,"kr_model_status":"CONNECTED_FROZEN_KR_REPLAY",
            "kr_replay_ready":True,"live_inference_enabled":False,"public_data_hashes_verified":True}

@app.get("/api/internal/model-replay/status")
def model_runtime_status():
    """Optional CPU artifact check; default web dependencies intentionally omit ML."""
    try:
        return model_replay_status()
    except (ModuleNotFoundError, FileNotFoundError, OSError):
        raise HTTPException(503,{"reason":"MODEL_DEPENDENCIES_NOT_INSTALLED","install":"requirements-model.txt"})
    except RuntimeError as exc:
        raise HTTPException(503,{"reason":str(exc)})

@app.get("/api/internal/model-replay/{code}")
def model_runtime_replay(code:str):
    """Exact 2023-12-28 demo-capsule replay, never arbitrary/live inference."""
    try:
        row=STATE.get("index",{}).get((code,"2023-12-28"))
        return replay_code(code,row)
    except ValueError as exc:
        raise HTTPException(422,{"reason":str(exc)})
    except KeyError as exc:
        raise HTTPException(404,{"reason":exc.args[0]})
    except (ModuleNotFoundError, FileNotFoundError, OSError):
        raise HTTPException(503,{"reason":"MODEL_DEPENDENCIES_NOT_INSTALLED","install":"requirements-model.txt"})
    except RuntimeError as exc:
        raise HTTPException(503,{"reason":str(exc)})

@app.get("/",include_in_schema=False)
@app.get("/kr",include_in_schema=False)
@app.get("/us",include_in_schema=False)
@app.get("/transfer",include_in_schema=False)
@app.get("/methodology",include_in_schema=False)
def page():
    return FileResponse(ROOT/"static/index.html")
