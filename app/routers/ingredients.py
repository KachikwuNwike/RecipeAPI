from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/recipes", tags=["Ingredients"])


@router.get("/{id}/ingredients")
def get_recipe_ingredients(id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id: {id} was not found",
        )
    return recipe.ingredients


@router.put("/{id}/ingredients")
def update_recipe_ingredients(
    id: int,
    updated_ingredients: schemas.Ingredients,
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

    recipe_query.update(
        {"ingredients": updated_ingredients.ingredients}, synchronize_session=False
    )
    db.commit()
    return recipe_query.first().ingredients
