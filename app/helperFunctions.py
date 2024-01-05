from app import models, schemas


def insert_cusine(cuisine_name: schemas.Cuisine, db, current_user):
    if not cuisine_name:
        return cuisine_name
    cuisine = db.query(models.Cuisine).filter_by(name=cuisine_name).first()
    if cuisine:
        return cuisine.cuisine_id
    else:
        new_cuisine = models.Cuisine(name=cuisine_name, owner_id=current_user.id)
        db.add(new_cuisine)
        db.commit()
        db.refresh(new_cuisine)
        return new_cuisine.cuisine_id


def insert_author(author_name: schemas.Author, db, current_user):
    if not author_name:
        return author_name
    author = db.query(models.Author).filter_by(name=author_name).first()
    if author:
        return author.author_id
    else:
        new_author = models.Author(name=author_name, owner_id=current_user.id)
        db.add(new_author)
        db.commit()
        db.refresh(new_author)
        return new_author.author_id


def insert_categories(categories, db, current_user):
    if not categories:
        return categories
    recipe_categories = []
    for category_name in categories:
        category = db.query(models.Category).filter_by(name=category_name).first()
        if not category:
            category = models.Category(name=category_name, owner_id=current_user.id)
            db.add(category)
            db.commit()
        recipe_categories.append(category)
    return recipe_categories
