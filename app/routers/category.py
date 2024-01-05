from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[schemas.CategoryOut])
def get_categories(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    categories = (
        db.query(models.Category)
        .filter(models.Category.name.ilike(f"%{search}%"))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return categories


@router.get("/{id}", response_model=schemas.CategoryOut)
def get_category(id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category).filter(models.Category.category_id == id).first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} was not found",
        )
    return category


@router.put("/{id}", response_model=schemas.CategoryOut)
def update_category(
    id: int,
    updated_category: schemas.Category,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    category_query = db.query(models.Category).filter(models.Category.category_id == id)
    category = category_query.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} was not found",
        )
    if category.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    try:
        category_query.update(updated_category.model_dump(), synchronize_session=False)
        db.commit()
        return category_query.first()
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Category, {updated_category.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    category_query = db.query(models.Category).filter(models.Category.category_id == id)
    category = category_query.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} was not found",
        )
    if category.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )
    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.CategoryOut
)
def add_category(
    category: schemas.Category,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_category = models.Category(owner_id=current_user.id, **category.model_dump())
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The Category, {new_category.name}, already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
