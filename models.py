from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """"User model"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    username = db.Column(
        db.String(30),
        unique = True, 
        nullable = False
    )

    email = db.Column(
        db.Text,
        unique = True,
        nullable = False
    )

    password = db.Column(
        db.Text,
        nullable = False
    )

    profile_image = db.Column(
        db.Text,
        default="/static/images/default-profile.png", 
    )

    grocery_lists = db.relationship(
        "List", 
        backref = "user", 
        cascade="all, delete-orphan"
    )

    saved_recipes = db.relationship(
        "Recipe",
        secondary = "saved_recipes",
        backref = "parents"
    )

    saved_ingredients = db.relationship(
        "Ingredient",
        secondary = "saved_ingredients",
        backref = "parents"
    )

    @classmethod
    def signup(cls, username, email, password, profile_image):

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            profile_image=profile_image,
        )

        db.session.add(user)
        
        return user

    @classmethod
    def validate(cls, username, password):

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Recipe(db.Model):
    """table for recipes"""

    __tablename__ = 'recipes'

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    recipe_id = db.Column(
        db.Integer,
        nullable = False
    )

    @classmethod
    def check_exists(cls, recipeId):
        """Checks if an ingredient is already stored in the database"""
        recipe = Recipe.query.filter_by(recipe_id = recipeId).first()

        if recipe == None:
            return False

        return recipe

class Saved_Recipe(db.Model):
    """"table to connect users to recipes"""

    __tablename__ = 'saved_recipes'

    user_saving_recipe = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete = 'cascade'),
        primary_key = True
    )

    recipe_saved = db.Column(
        db.Integer,
        db.ForeignKey('recipes.id', ondelete = 'cascade'),
        primary_key = True
    )

class Ingredient(db.Model):
    """Table for ingredients"""

    __tablename__ = 'ingredients'

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    ingredient_id = db.Column(
        db.String(100),
        nullable = False
    )

    @classmethod
    def check_exists(cls, foodId):
        """Checks if an ingredient is already stored in the database"""
        ingredient = Ingredient.query.filter_by(ingredient_id = foodId).first()

        if ingredient == None:
            return False

        return ingredient

    
class Saved_Ingredient(db.Model):
    """Table to connect users to saved ingredients"""

    __tablename__ = 'saved_ingredients'

    user_saving_ingredient = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete = 'cascade'),
        primary_key = True
    )

    ingredient_saved = db.Column(
        db.Integer,
        db.ForeignKey('ingredients.id', ondelete = 'cascade'),
        primary_key = True
    )

class List(db.Model):
    """table for grocery lists"""

    __tablename__ = "lists"

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

# class List_Ingredient:
#     """"Table for joining ingredients to lists"""

#     ___tablename__ = "list_ingredients"

#     list_id = db.Column(
#         db.Integer,
#         db.ForeignKey('lists.id', ondelete = 'cascade'),
#         primary_key = True
#     )

#     ingredient_id = db.Column(
#         db.Integer,
#         db.ForeignKey('ingredients.id', ondelete = 'cascade'),
#         primary_key = True
#     )


def connect_db(app):
    db.app = app
    db.init_app(app)
    