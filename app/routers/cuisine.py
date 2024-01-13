from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/cuisines", tags=["Cuisines"])


@router.get("/", response_model=List[schemas.CuisineOut])
def get_cuisines(
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    search: Optional[str] = "",
):
    cuisines = (
        db.query(models.Cuisine)
        .filter(models.Cuisine.name.ilike(f"%{search}%"))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return cuisines


@router.get("/{id}", response_model=schemas.CuisineOut)
def get_cuisine(id: int, db: Session = Depends(get_db)):
    cuisine = db.query(models.Cuisine).filter(models.Cuisine.cuisine_id == id).first()
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuisine with id: {id} was not found",
        )
    return cuisine


@router.put("/{id}", response_model=schemas.CuisineOut)
def update_cuisine(
    id: int,
    updated_cuisine: schemas.Cuisine,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    cuisine_query = db.query(models.Cuisine).filter(models.Cuisine.cuisine_id == id)
    cuisine = cuisine_query.first()
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuisine with id: {id} was not found",
        )

    if cuisine.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    try:
        cuisine_query.update(updated_cuisine.model_dump(), synchronize_session=False)
        db.commit()
        return cuisine_query.first()
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Cuisine, {updated_cuisine.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cuisine(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    cuisine_query = db.query(models.Cuisine).filter(models.Cuisine.cuisine_id == id)
    cuisine = cuisine_query.first()
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuisine with id: {id} was not found",
        )

    if cuisine.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    recipes_with_cuisine = (
        db.query(models.Recipe).filter(models.Recipe.cuisine_id == id).all()
    )
    for recipe in recipes_with_cuisine:
        recipe.cuisine_id = None
    db.delete(cuisine)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.CuisineOut
)
def add_cusine(
    cuisine: schemas.Cuisine,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_cuisine = models.Cuisine(owner_id=current_user.id, **cuisine.model_dump())
    db.add(new_cuisine)
    try:
        db.commit()
        db.refresh(new_cuisine)
        return new_cuisine
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Cuisine, {new_cuisine.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
