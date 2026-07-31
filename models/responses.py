from pydantic import BaseModel


class Post(BaseModel):
    id: int
    title: str
    body: str
    userId: int


class User(BaseModel):
    id: int
    name: str
    username: str
    email: str


class Comment(BaseModel):
    postId: int
    id: int
    name: str
    email: str
    body: str
