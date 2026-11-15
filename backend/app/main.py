from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
from alembic.script import ScriptDirectory
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .config import get_settings
from . import auth, demo, finance, giving, portfolio, advisor, ads, market, ai_connections

config = get_settings()
MIGRATION_HEADS = set(ScriptDirectory(str(Path(__file__).resolve().parents[1] / 'alembic')).get_heads())
app = FastAPI(title='Barakah API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=config.origins, allow_credentials=True, allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'], allow_headers=['Authorization', 'Content-Type', 'X-CSRF-Token'])


@app.middleware('http')
async def browser_security(request: Request, call_next):
    origin = request.headers.get('origin')
    if request.method not in {'GET', 'HEAD', 'OPTIONS'} and origin and origin not in config.origins:
        return JSONResponse({'error': {'code': 'origin_forbidden', 'message': 'Untrusted request origin'}}, status_code=403)
    size = request.headers.get('content-length')
    if size and (not size.isdigit() or int(size) > 65536):
        return JSONResponse({'error': {'code': 'request_too_large', 'message': 'Request body too large'}}, status_code=413)
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 65536:
                return JSONResponse({'error': {'code': 'request_too_large', 'message': 'Request body too large'}}, status_code=413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    if config.environment == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.exception_handler(StarletteHTTPException)
async def http_error(request, exc):
    detail = exc.detail if isinstance(exc.detail, dict) and 'code' in exc.detail else {'code': 'http_error', 'message': str(exc.detail)}
    return JSONResponse({'error': detail}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo request values (passwords, tokens, chat or financial records).
    if request.url.path.startswith('/api/v1/ai/connection'):
        return JSONResponse({'error': {'code': 'validation_error', 'message': 'Check the AI connection fields.'}}, status_code=422)
    fields = sorted({'.'.join(str(part) for part in error['loc'][1:]) or 'request' for error in exc.errors()})
    return JSONResponse({'error': {'code': 'validation_error', 'message': 'Check these fields: ' + ', '.join(fields)}}, status_code=422)


@app.exception_handler(IntegrityError)
async def conflict(request, exc):
    return JSONResponse({'error': {'code': 'conflict', 'message': 'Resource conflicts with an existing record or constraint'}}, status_code=409)


@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    # Handled before Starlette's server-error rethrow; never log bound parameters.
    return JSONResponse({'error': {'code': 'database_unavailable', 'message': 'Database operation unavailable; please retry later'}}, status_code=503)


@app.exception_handler(Exception)
async def internal_error(request, exc):
    return JSONResponse({'error': {'code': 'internal_error', 'message': 'An unexpected server error occurred'}}, status_code=500)


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/v1/health')
def readiness():
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    from . import db as database
    try:
        with database.SessionLocal() as session:
            applied = set(session.execute(text('SELECT version_num FROM alembic_version')).scalars())
            if applied != MIGRATION_HEADS:
                return JSONResponse({'status': 'unavailable', 'database': 'migration_required'}, status_code=503)
            session.execute(text('SELECT id FROM users LIMIT 1'))
    except SQLAlchemyError:
        return JSONResponse({'status': 'unavailable', 'database': 'unavailable'}, status_code=503)
    return {'status': 'ready', 'database': 'available', 'external_services': 'check /api/v1/ai/health separately'}


for router in (auth.router, demo.router, finance.router, giving.router, portfolio.router, advisor.router, ads.router, market.router, ai_connections.router):
    app.include_router(router, prefix='/api/v1')


if config.frontend_dist:
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    frontend = Path(config.frontend_dist).resolve()
    if not (frontend / 'index.html').is_file():
        raise RuntimeError('Build barakah-ui before enabling FRONTEND_DIST')

    @app.api_route('/api/{path:path}', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def unknown_api(path: str):
        raise HTTPException(404, 'API endpoint not found')

    @app.get('/reset-password')
    def reset_page():
        return FileResponse(frontend / 'index.html')

    app.mount('/', StaticFiles(directory=frontend, html=True), name='frontend')
