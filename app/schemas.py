from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, EmailStr, conlist, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Author(BaseModel):
    name: constr(to_lower=True)
    bio: Optional[str] = None


class AuthorOut(Author):
    author_id: int

    class Config:
        from_attributes = True


class Category(BaseModel):
    name: constr(to_lower=True)


class CategoryOut(Category):
    category_id: int

    class Config:
        from_attributes = True


class CategoryInDB(BaseModel):
    category_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Cuisine(BaseModel):
    name: constr(to_lower=True)


class CuisineOut(Cuisine):
    cuisine_id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: constr(to_lower=True)
    url: Optional[str] = None
    description: Optional[str] = None
    servings: Optional[str] = None
    nutrition_facts: Optional[dict] = None
    ingredients: list
    direction: Optional[dict] = None
    prep_time: Optional[timedelta] = None
    cook_time: Optional[timedelta] = None
    total_time: Optional[timedelta] = None
    image_link: Optional[str] = None
    video_link: Optional[str] = None


class Recipe(RecipeBase):
    cuisine: Optional[str] = None
    author: Optional[str] = None
    category: Optional[list[constr(to_lower=True)]] = None


class RecipeInDB(RecipeBase):
    cuisine_id: int
    author_id: int


class RecipeOutDB(RecipeBase):
    recipe_id: int
    categories: list[CategoryOut]
    author: Optional[AuthorOut] = None
    cuisine: Optional[CuisineOut] = None

    class Config:
        from_attributes = True


class Ingredients(BaseModel):
    ingredients: conlist(str, min_length=1)


class Direction(BaseModel):
    direction: dict
