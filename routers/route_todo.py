#routerを有効にする
from fastapi import APIRouter
#Request, Responseをインポートすることで、APIのパスオペレーション関数の引数として使える
from fastapi import Request, Response, HTTPException, Depends
#jsonをエンコード
from fastapi.encoders import jsonable_encoder
from schemas import Todo, TodoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_get_single_todo, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf


#インスタンス化
router = APIRouter()
auth = AuthJwtCsrf()

#routerを使ってエンドポイントを定義する
#response_modelを指定することで、レスポンスのモデルを指定できる schema.pyのTodoを指定している
@router.post("/api/todo", response_model=Todo)
async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}", httponly=True,
        samesite="none", secure=True
    )
    if res:
        return res
    raise HTTPException(status_code=404, detail="Create task failed")

#タスクの一覧を取得するエンドポイント
@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request):
    auth.verify_jwt(request) #Renderにデプロイする際にコメントアウト
    res = await db_get_todos()
    return res

#特定のIDに基づいて一つのタスクを取得するエンドポイント
@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(request: Request, response: Response, id: str):
    new_token, _ = auth.verify_update_jwt(request)
    res = await db_get_single_todo(id)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}", httponly=True,
        samesite="none", secure=True
    )
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"Task of ID:{id} does't exist")

#アップデート更新するエンドポイント
@router.put("/api/todo/{id}", response_model=Todo)
async def update_todo(request: Request, response: Response, id: str, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, todo)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}", httponly=True,
        samesite="none", secure=True
    )
    if res:
        return res
    raise HTTPException(status_code=404, detail="Update task failed")

#デリートするエンドポイント
@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    res = await db_delete_todo(id)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}", httponly=True,
        samesite="none", secure=True
    )
    if res:
        return {"message": 'Successfully deleted'}
    raise HTTPException(status_code=404, detail="Delete task failed")

