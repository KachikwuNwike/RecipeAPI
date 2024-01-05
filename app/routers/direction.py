from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/recipes", tags=["Directions"])


@router.get("/{id}/direction")
def get_recipe_direction(id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {id} was not found",
        )
    return recipe.direction


@router.put("/{id}/direction")
def update_recipe_direction(
    id: int,
    updated_direction: schemas.Direction,
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

    if not updated_direction.direction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Empty direction. Please provide valid data.",
        )
    else:
        recipe_query.update(
            {"direction": updated_direction.direction}, synchronize_session=False
        )
        db.commit()
        return recipe_query.first().direction


@router.delete("/{id}/direction", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_ingredients(
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

    recipe_query.update({"direction": None}, synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
