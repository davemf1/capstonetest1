import os


from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import LoginForm, RegisterForm
from models import User, Ingredient, Saved_Ingredient, Recipe, Saved_Recipe
import requests
import json
from collections.abc import Mapping


from models import db, connect_db

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "development uri")
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('DATABASE_URL', 'postgresql://postgres:' + databaseKey + '@localHost:5432/thefridge2'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
IngredientAPIKey = os.environ.get("IngredientAPIKey", "ingredient key")
MealApiKey3 = os.environ.get("MealApiKey3", "meal  key")



connect_db(app)
db.create_all()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/')
def index():

    if g.user:
        return redirect("/users")
        
    return render_template("index.html")

def do_login(user):
    """Stores user in session"""

    session[CURR_USER_KEY] = user.id
    

def do_logout():
    """Deletes user from Session"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handles user login"""
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.validate(form.username.data,form.password.data)

        if user:
            do_login(user)
            return redirect("/users")

        flash("Invalid credentials.", 'danger')

    return render_template("login.html", form=form)

@app.route("/logout" , methods=["GET"])
def logout():
    """Calls logout function then redirects to index"""

    do_logout()
    return redirect('/')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handles user register and adds them to the database"""
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                profile_image=form.profile_image.data or User.profile_image.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/users")

    else:
        return render_template('signup.html', form=form)

@app.route("/users", methods=["GET"])
def home():
    """Home page for logged in users"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    return render_template("home.html")
    
@app.route("/ingredients", methods=["GET"])
def ingredient_page():
    """Returns page to allow users to add ingredients to their fridge"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")
    
    return render_template("ingredient.html")

@app.route("/users/saved_ingredients", methods=["GET"])
def get_saved_ingredients():
    """Gets all users saved ingredients then returns an array of all ingredients"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)

    saved_ingredients = [ingredient.ingredient_id for ingredient in user.saved_ingredients]

    return jsonify(saved_ingredients)

@app.route("/users/ingredients/add/<foodId>", methods=["POST", "GET"])
def add_ingredients(foodId):
    """Adds ingredients to users data"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")
    
    ingredient = Ingredient.check_exists(foodId)

    if ingredient in g.user.saved_ingredients:
        return "exists"

    if ingredient:
        g.user.saved_ingredients.append(ingredient)
        db.session.commit()
        return "Success"
    
    else:
        ingredient = Ingredient(ingredient_id = foodId)
        db.session.add(ingredient)
        g.user.saved_ingredients.append(ingredient)
        db.session.commit()
        return "Success"

@app.route("/users/ingredients/remove/<foodId>", methods=["GET", "POST"])
def remove_ingredients(foodId):
    """Remove ingredients from users data"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    ingredient = Ingredient.query.filter_by(ingredient_id = foodId).first()

    g.user.saved_ingredients.remove(ingredient)
    db.session.commit()

    return "Success"

@app.route('/users/recipes/add/<recipeId>', methods=["GET", "POST"])
def add_recipe(recipeId):
    """Adds recipe to users data"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")
    
    recipe = Recipe.check_exists(recipeId)

    if recipe in g.user.saved_recipes:
        return "exists"

    if recipe:
        g.user.saved_recipes.append(recipe)
        db.session.commit()
        return "Success"
    
    else:
        recipe = Recipe(recipe_id = recipeId)
        db.session.add(recipe)
        g.user.saved_recipes.append(recipe)
        db.session.commit()
        return "Success"

@app.route("/users/recipes/remove/<recipeId>", methods=["GET", "POST"])
def remove_recipe(recipeId):
    """Remove recipe from users data"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    recipe = Recipe.query.filter_by(recipe_id = recipeId).first()

    g.user.saved_recipes.remove(recipe)
    db.session.commit()

    return "Success"

@app.route("/ingredients/search/<query>", methods=["GET"])
def search_ingredients(query):
    """Calls to ingredient API and returns an ingeredient to user"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    url = "https://edamam-food-and-grocery-database.p.rapidapi.com/parser"

    querystring = {"ingr":query}

    headers = {
        "X-RapidAPI-Key": IngredientAPIKey,
        "X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

@app.route("/recipes/search", methods=["GET", "POST"])
def search_recipes():
    """Calls to recipe API and returns recipe/s to user"""
    

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/") 

    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

    querystring = {"query": request.args["recipeType"], "includeIngredients": request.args["ingredients"]}

    headers = {
	"X-RapidAPI-Key": MealApiKey3,
	"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

@app.route("/users/recipes", methods=["GET", "POST"])
def recipes():
    """Returns recipe page"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/") 

    return render_template("recipes.html")

@app.route('/recipes/get/<int:recipeId>')
def get_recipe(recipeId):
    """returns info on a single recipe"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/") 

    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{recipeId}/information".format(recipeId = recipeId)

    headers = {
        "X-RapidAPI-Key": MealApiKey3,
        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    return response.text

@app.route("/users/saved_recipes", methods=["GET"])
def get_saved_recipes():
    """Gets all users saved recipes then returns an array of all recipes"""

    if not g.user:
        flash("You must be logged in to continue", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)

    saved_recipes = [recipe.recipe_id for recipe in user.saved_recipes]

    return jsonify(saved_recipes)
    
@app.route("/favicon.ico")
def favicon():
    return