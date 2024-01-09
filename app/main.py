from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models

from .database import engine
from .routers import (
    auth,
    author,
    category,
    cuisine,
    direction,
    ingredients,
    recipe,
    user,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(recipe.router)
app.include_router(author.router)
app.include_router(category.router)
app.include_router(cuisine.router)
app.include_router(ingredients.router)
app.include_router(direction.router)


@app.get("/")
def root():
    return {"message": "Welcome to Recipe API"}
