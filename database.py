#環境変数を読み込む
from decouple import config

from fastapi import HTTPException

#返り値が、dictかfalseの可能性があるので型はUnionを使う
from typing import Union

#MongoDBと連携
import motor.motor_asyncio

#mongoDBのidを特定する為に必要
from bson import ObjectId

#auth_utils.pyからAuthJwtCsrfクラスをインポート
from auth_utils import AuthJwtCsrf

#Renderにデプロイする為に追加
import asyncio


MONGO_API_KEY = config('MONGO_API_KEY')

#MongoDBのクライアントを作成
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
#Renderにデプロイする為に追加
client.get_io_loop = asyncio.get_event_loop

#MongoDBのデータベースを作成
database = client.API_DB
collection_todo = database.todo
collection_user = database.user
auth = AuthJwtCsrf()

#MongoDBのタスクのアイテムを作成
#motorにinsert_oneを使うと、_idが返ってくる
#insert_oneの返り値は、InsertOneResultクラスのインスタンス クラスの属性にinserted_idがあり、これが_idになる
#mongoDBからfind_oneでidを特定して取得
#find_oneのリターンのタイプはmotorのドキュメント参照 対象のドキュメントが存在する場合はドキュメントを返し、存在しない場合はNoneが返る それをif文で判定 リターンするidは日付などあり、複雑な為辞書型に変換するシリアライザーが必要 辞書型かFalseを返すのでUnionを使う
#mongoDBのidは、_idであることに注意

#辞書型に変換する為のシリアライザー
def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"]
    }
#userのシリアライザー
def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"]
    }


async def db_create_todo(data: dict) -> Union[dict, bool]:
    todo = await collection_todo.insert_one(data)
    new_todo = await collection_todo.find_one({"_id": todo.inserted_id})
    if new_todo:
        return todo_serializer(new_todo)
    return False

#mongoDBからfindを使って全てのドキュメントを取得
#motorのfindは、to_listでリストに変換する
async def db_get_todos() -> list:
    todos = []
    for todo in await collection_todo.find().to_list(length=100):
        todos.append(todo_serializer(todo))
    return todos

#mongoDBからfind_oneでidを特定して取得
async def db_get_single_todo(id: str) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        return todo_serializer(todo)
    return False

#アップデート
#mongoDBのupdate_oneを使う
#update_oneの第一引数は、更新するドキュメントの条件を指定する
#第二引数は、更新する内容を指定する
#第三引数は、更新したドキュメントを返すかどうかを指定する
#modified_countは、更新したドキュメントの数を返す
async def db_update_todo(id: str, data: dict) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        updated_todo = await collection_todo.update_one({"_id": ObjectId(id)}, {"$set": data})
        if (updated_todo.modified_count > 0):
            new_todo = await collection_todo.find_one({"_id": ObjectId(id)})
            return todo_serializer(new_todo)
    return False

#削除
#mongoDBのdelete_oneを使う
#delete_oneの第一引数は、削除するドキュメントの条件を指定する
#第二引数は、削除したドキュメントを返すかどうかを指定する
#deleted_countは、削除したドキュメントの数を返す
async def db_delete_todo(id: str) -> bool:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        deleted_todo = await collection_todo.delete_one({"_id": ObjectId(id)})
        if (deleted_todo.deleted_count > 0):
            return True
        return False

#ユーザー新規登録
#user email重複判定
#mongoDBのinsert_oneを使う
async def db_signup(data: dict) -> dict:
    email = data.get("email")
    password = data.get("password")
    overlap_user = await collection_user.find_one({"email": email})
    if overlap_user:
        raise HTTPException(status_code=400, detail="Email is already taken")
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    user = await collection_user.insert_one({"email": email, "password": auth.generate_hashed_pw(password)})
    new_user = await collection_user.find_one({"_id": user.inserted_id})
    return user_serializer(new_user)

#ユーザーログイン
#mongoDBのfind_oneを使う
async def db_login(data: dict) -> str:
    email = data.get("email")
    password = data.get("password")
    user = await collection_user.find_one({"email": email})
    if not user or not auth.verify_pw(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.encode_jwt(user["email"])
    return token



