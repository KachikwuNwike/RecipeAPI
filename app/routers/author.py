from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.helperFunctions import insert_categories, insert_cusine

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("/", response_model=List[schemas.AuthorOut])
def get_authors(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    authors = (
        db.query(models.Author)
        .filter(models.Author.name.ilike(f"%{search}%"))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return authors


@router.get("/{id}", response_model=schemas.AuthorOut)
def get_author(id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.author_id == id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )
    return author


@router.put("/{id}", response_model=schemas.AuthorOut)
def update_author(
    id: int,
    updated_author: schemas.Author,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    author_query = db.query(models.Author).filter(models.Author.author_id == id)
    author = author_query.first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )

    if author.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    updated_author.name = author.name
    try:
        author_query.update(updated_author.model_dump(), synchronize_session=False)
        db.commit()
        return author_query.first()
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Author, {updated_author.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    author_query = db.query(models.Author).filter(models.Author.author_id == id)
    author = author_query.first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )
    if author.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    db.query(models.Recipe).filter(models.Recipe.author_id == id).update(
        {"author_id": None}
    )
    db.delete(author)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.AuthorOut)
def add_author(
    author: schemas.Author,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_author = models.Author(owner_id=current_user.id, **author.model_dump())
    db.add(new_author)
    try:
        db.commit()
        db.refresh(new_author)
        return new_author
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Author, {new_author.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


@router.get("/{id}/recipes", response_model=List[schemas.RecipeOutDB])
def get_author_recipes(
    id: int,
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    author = db.query(models.Author).filter(models.Author.author_id == id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.author_id == id)
        .filter(models.Recipe.name.ilike(f"%{search}%"))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return recipes


@router.get("/{id}/categories", response_model=List[schemas.CategoryOut])
def get_author_categories(id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.author_id == id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )

    categories = (
        db.query(models.Category)
        .join(
            models.recipe_category,
            models.Category.category_id == models.recipe_category.c.category_id,
        )
        .join(
            models.Recipe, models.Recipe.recipe_id == models.recipe_category.c.recipe_id
        )
        .filter(models.Recipe.author_id == id)
        .all()
    )
    return categories


@router.post(
    "/{id}/recipes",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RecipeOutDB,
)
def add_author_recipe(
    id: int,
    recipe: schemas.Recipe,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    author = db.query(models.Author).filter(models.Author.author_id == id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {id} was not found",
        )

    recipe_found = (
        db.query(models.Recipe)
        .filter(models.Recipe.name == recipe.name, models.Recipe.author_id == id)
        .first()
    )
    if recipe_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The Recipe, {recipe.name}, by {author.name} already exists",
        )

    cuisine_id = insert_cusine(recipe.cuisine, db, current_user)
    author_id = author.author_id
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


@router.put("/{authorId}/recipes/{recipeId}", response_model=schemas.RecipeOutDB)
def update_author_recipe(
    authorId: int,
    recipeId: int,
    updated_recipe: schemas.Recipe,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    author = db.query(models.Author).filter(models.Author.author_id == authorId).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {authorId} was not found",
        )

    recipe_query = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipeId)
    recipe = recipe_query.first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {recipeId} was not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    updated_recipe.name = recipe.name
    cuisine_id = insert_cusine(updated_recipe.cuisine, db, current_user)
    author_id = authorId
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


@router.delete("/{authorId}/recipes/{recipeId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author_recipe(
    authorId: int,
    recipeId: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    author = db.query(models.Author).filter(models.Author.author_id == authorId).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id: {authorId} was not found",
        )

    recipe_query = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipeId)
    recipe = recipe_query.first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {recipeId} was not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
