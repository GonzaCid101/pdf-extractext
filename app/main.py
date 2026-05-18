"""Entry point de la aplicación FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.endpoints.pdfs import router as pdfs_router
from app.api.endpoints.upload import router as upload_router
from app.api.health import router as health_router
from app.core.config import settings
from app.exceptions.rfc9457 import RFC9457Exception

app = FastAPI(title=settings.APP_TITLE)


@app.exception_handler(RFC9457Exception)
async def rfc9457_exception_handler(request: Request, exc: RFC9457Exception):
    return JSONResponse(
        status_code=exc.status,
        content=exc.to_dict(),
        media_type="application/problem+json",
    )


app.include_router(health_router)
app.include_router(upload_router)
app.include_router(pdfs_router)
