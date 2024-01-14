# Recipe API

Welcome to RecipeAPI! This FastAPI-powered RESTful API with user authentication enables users to access detailed recipe information based on various criteria such as recipe author and cuisine.

Explore the API: https://recipeapi-kachikwu-37473924f8f6.herokuapp.com/docs

## Features

- **Recipe Exploration:** Browse and search through a wide variety of recipes.
- **Detailed Information:** Access comprehensive details about recipes, including ingredients and cuisine.
- **User Authentication:** Ensure user security through JWT (JSON Web Tokens) token-based authentication.
- **Database Management:** Seamlessly handle database migrations with Alembic.

## Technology Used

The technologies utilized in this project include:

- **FastAPI:** A modern, fast web framework for building APIs with Python.
- **Alembic:** Database migration tool for SQLAlchemy.
- **SQLAlchemy:** SQL toolkit and Object-Relational Mapping (ORM) library.
- **PostgreSQL:** A powerful, open-source relational database system.

<h2>Project Structure</h2>

The project follows the structure below:

- **alembic:** Database migration scripts.
- **app:**
  - **routers:** API route handlers.
  - **schemas:** Pydantic models for API request/response validation.
  - **models:** SQLAlchemy table models.
  - **oauth2:** User authentication and authorization components using JWT.
  - **main.py:** Entry point for the FastAPI application.
  - **config.py:** Configuration settings.
