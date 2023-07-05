from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
#cors
from fastapi.middleware.cors import CORSMiddleware
from routers import route_todo, route_auth
from schemas import SuccessMsg, CsrfSettings
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

app = FastAPI()
#routerを登録する
app.include_router(route_todo.router)
app.include_router(route_auth.router)
#white list （本番環境では変更する）
origins = ['http://localhost:3000','https://demo-fastapi3.onrender.com']
#corsの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#CSRFの設定
@CsrfProtect.load_config
def get_csrf_config():
  return CsrfSettings()

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
  return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.get("/", response_model=SuccessMsg)
def root():
    return {"message": "welcome to the api"}
