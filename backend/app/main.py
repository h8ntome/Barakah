from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .config import get_settings
from . import auth, finance, giving, portfolio, advisor, ads

config = get_settings()
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
    return JSONResponse({'error': {'code': 'validation_error', 'message': 'Invalid request fields; consult API schema'}}, status_code=422)


@app.exception_handler(IntegrityError)
async def conflict(request, exc):
    return JSONResponse({'error': {'code': 'conflict', 'message': 'Resource conflicts with an existing record or constraint'}}, status_code=409)


@app.exception_handler(Exception)
async def internal_error(request, exc):
    return JSONResponse({'error': {'code': 'internal_error', 'message': 'An unexpected server error occurred'}}, status_code=500)


@app.get('/health')
def health():
    return {'status': 'ok'}


for router in (auth.router, finance.router, giving.router, portfolio.router, advisor.router, ads.router):
    app.include_router(router, prefix='/api/v1')
