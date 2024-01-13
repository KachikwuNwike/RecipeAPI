from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.helperFunctions import insert_author, insert_categories, insert_cusine

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=List[schemas.RecipeOutDB])
def get_recipes(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    author: Optional[str] = "",
    cuisine: Optional[str] = "",
):
    recipes = (
        db.query(models.Recipe)
        .join(models.Author, models.Author.author_id == models.Recipe.author_id)
        .join(models.Cuisine, models.Cuisine.cuisine_id == models.Recipe.cuisine_id)
        .filter(models.Recipe.name.ilike(f"%{search}%"))
        .filter(models.Author.name.ilike(f"%{author}%"))
        .filter(models.Cuisine.name.ilike(f"%{cuisine}%"))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return recipes


@router.get("/{id}", response_model=schemas.RecipeOutDB)
def get_recipe(id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {id} was not found",
        )
    return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.recipe_id == id)
    recipe = recipe_query.first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {id} was not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.RecipeOutDB
)
def add_recipe(
    recipe: schemas.Recipe,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    recipe_found = (
        db.query(models.Recipe).filter(models.Recipe.name == recipe.name).first()
    )
    if recipe_found:
        if recipe.author and (recipe_found.author.name == recipe.author):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Recipe, {recipe.name}, by {recipe.author} already exists",
            )

    cuisine_id = insert_cusine(recipe.cuisine, db, current_user)
    author_id = insert_author(recipe.author, db, current_user)
    categories = insert_categories(recipe.category, db, current_user)

    recipe_in = schemas.RecipeInDB(
        **recipe.model_dump(), cuisine_id=cuisine_id, author_id=author_id
    )

    if categories:
        new_recipe = models.Recipe(
            owner_id=current_user.id, **recipe_in.model_dump(), categories=categories
        )
    elif not categories:
        new_recipe = models.Recipe(owner_id=current_user.id, **recipe_in.model_dump())

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe


@router.put("/{id}", response_model=schemas.RecipeOutDB)
def update_recipe(
    id: int,
    updated_recipe: schemas.Recipe,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.recipe_id == id)
    recipe = recipe_query.first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {id} was not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    updated_recipe.name = recipe.name
    cuisine_id = insert_cusine(updated_recipe.cuisine, db, current_user)
    author_id = recipe.author_id
    categories = insert_categories(updated_recipe.category, db, current_user)

    updated_recipe_in = schemas.RecipeInDB(
        **updated_recipe.model_dump(), cuisine_id=cuisine_id, author_id=author_id
    )

    recipe_query.update(updated_recipe_in.model_dump(), synchronize_session=False)
    if categories:
        recipe_query.first().categories = categories
    elif not categories:
        recipe_query.first().categories = []
    db.commit()
    return recipe_query.first()
