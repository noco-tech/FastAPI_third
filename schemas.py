#型を定義するにはfastapiのBaseModelを継承する
# ここで定義した型は、APIのパスオペレーション関数の引数として使える
# また、APIのレスポンスモデルとしても使える

from pydantic import BaseModel
from typing import Optional

#CSRFの設定
from decouple import config
CSRF_KEY = config('CSRF_KEY')
class CsrfSettings(BaseModel):
    secret_key: str = CSRF_KEY

class Csrf(BaseModel):
    csrf_token: str


#エンドポイントが受け取るリクエストボディの型を定義
class Todo(BaseModel):
    id: str
    title: str
    description: str

#エンドポイントが返すレスポンスボディの型を定義
class TodoBody(BaseModel):
    title: str
    description: str

#main.pyで使うレスポンスモデルを定義
#レスポンスモデルは、APIのレスポンスボディの型を定義する
class SuccessMsg(BaseModel):
    message: str

#userの型 frontendから受け取るリクエストボディの型を定義
class UserBody(BaseModel):
    email: str
    password: str

#restAPIのレスポンス 複数のエンドポイントで使う
class UserInfo(BaseModel):
    id: Optional[str] = None
    email: str

