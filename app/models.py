from sqlalchemy import (
    ARRAY,
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table,
    Text,
    Time,
    text,
)
from sqlalchemy.orm import relationship

from .database import Base

recipe_category = Table(
    "recipe_category",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.recipe_id", ondelete="CASCADE")),
    Column(
        "category_id", Integer, ForeignKey("categories.category_id", ondelete="CASCADE")
    ),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    phone_number = Column(String)


class Author(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    bio = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Cuisine(Base):
    __tablename__ = "cuisines"

    cuisine_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id = Column(Integer, primary_key=True, nullable=False)

    name = Column(String(255), nullable=False)

    url = Column(String(255))

    cuisine_id = Column(Integer, ForeignKey("cuisines.cuisine_id"))
    cuisine = relationship("Cuisine")

    author_id = Column(Integer, ForeignKey("authors.author_id"))
    author = relationship("Author")

    categories = relationship("Category", secondary=recipe_category)

    description = Column(Text)

    servings = Column(String(50))

    nutrition_facts = Column(JSON)

    ingredients = Column(ARRAY(String))

    direction = Column(JSON)

    prep_time = Column(Interval)
    cook_time = Column(Interval)
    total_time = Column(Interval)

    image_link = Column(String(255))
    video_link = Column(String(255))

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
