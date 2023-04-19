

$("#ingredientSearch").on("change", function(){
    // Make a request to search for ingredients
    if ($("#ingredientSearch").val() != ""){
        axios.get('/ingredients/search/' + $("#ingredientSearch").val())
        .then(function (response) {
            // handle success
            $("#ingredient-container").empty();
            const ingredients = response.data.hints
            for(const ingredient of ingredients){
                $("#ingredient-container").append(`
                    <div class='col-lg-3 col-md-4 col-6 my-auto'>
                    <div class='ingredient-card'>
                    <img src='${ingredient.food.image || "/static/images/default-ingredient-img.png"}' alt='food image'/>
                    <h6>${ingredient.food.label}</h6>
                    <i data-food-id ='${ingredient.food.foodId}' class="add-ingredient btn btn-secondary">Add</i>
                    </div>
                    </div
                    `
                )
            }
        })
        .catch(function (error) {
            // handle error
            $("#ingredient-container").empty();
            $("#ingredient-container").html(
                "<p>Something went wrong please try again</p>"
            )
        })
    }

});

$("#ingredient-container").on("click", "i", function(e){
    const foodId = $(this)[0].dataset.foodId;
    const parentElem = $(this).parent();
    
    if ($(this).hasClass("add-ingredient") == true){
        axios.get(`/users/ingredients/add/${foodId}`)
        .then(function (response) {
            if (response.data == "Success"){
                parentElem.html("<p>Ingredient Saved!</p>")
                
            }
            else if(response.data == "exists"){
                parentElem.html("<p>This ingredient is already in your fridge</p>")
            }
        })
        .catch(function (error) {
            $('.results').text("Something Went wrong please try again later");
        })
    }

    else if($(this).hasClass("remove-ingredient") == true){
        axios.get(`/users/ingredients/remove/${foodId}`)
        .then(function (response) {
            if (response.data == "Success"){
                parentElem.html("<p>Ingredient Removed!</p>")
            }
        })
        .catch(function (error) {
            $('.results').text("Something Went wrong please try again later");
        })
    }

    else if($(this).hasClass("add-to-pot") == true){
        $("#pot-container").append(parentElem.parent());
        parentElem.children(".add-to-pot").hide();
        parentElem.children("p").hide();
        $(".results2").empty();
    }

});

$("#pot-container").on("click", "i", function(e){
    const parentElem = $(this).parent();
    $("#ingredient-container").append(parentElem.parent());
    parentElem.children(".add-to-pot").show();
    parentElem.children("p").show();
    
});

$(".find-recipe").on("click", function(e){
    e.preventDefault();
    $("#recipeType").css("border", "1px solid lightgray")
    if($("#recipeType").val() == ""){
        $("#recipeType").css("border", "1px solid red")
        return false;
    }
    let $allIngredientCards = $("#pot-container").find("h6");

    let potIngredients = [];
    
    for(let ingredient of $allIngredientCards){
        potIngredients.push(ingredient.innerText);
    }

    if(potIngredients.length == 0 ){
        $(".results2").text("Please add ingredients to continue")
        return false;
    }

    potIngredients.reduce((f, s) => `${f},${s}`)
    potIngredients = potIngredients.toString();
    
    axios.get('/recipes/search', {params: {ingredients: potIngredients, recipeType: $("#recipeType").val()}})
        .then(function (response) {
            // const results = response.data.results;

           for(const result of response.data.results){
            $(".recipe-container").append(`
                <div class='col-lg-3 col-md-4 col-6 my-auto'>
                <div class='recipe-card'>
                <img src='${result.image || "/static/images/default-ingredient-img.png"}' alt='food image'/>
                <h6>${result.title}</h6>
                <i data-food-id ='${result.id}' class="btn btn-secondary save-recipe">Save Recipe</i>
                <i data-food-id ='${result.id}' class="btn btn-secondary more-info">More Info</i>
                </div>
                </div
            `
           )
           }
           
           $(".ingredients").hide();
           $(".recipes").show();
        })
        .catch(function (error) {
            // handle error
        })
});

$(".recipes").on("click", ".ingredient-back-btn", function(){

    $(".recipe-container").empty();
    $(".recipes").hide();
    $(".ingredients").show();
});


$(".recipes").on("click", ".save-recipe", function(){
    const recipeId = $(this)[0].attributes[0].nodeValue;
    const parentElem = $(this).parent();
    axios.get(`/users/recipes/add/${recipeId}`)
        .then(function (response) {
            if (response.data == "Success"){
                parentElem.html("<p>Recipe Saved!</p>")
            }
            else if(response.data == "exists"){
                parentElem.html("<p>This recipe is already saved</p>")
            }
        })
        .catch(function (error) {
            $('.results3').text("Something Went wrong please try again later");
        })
})

function recipeModal(response){
    $(".modal1-content").children().empty();
        const recipeSteps = response.data.analyzedInstructions[0].steps;
        const ingredientList = response.data.extendedIngredients;
        const recipeTitle = response.data.title;
        const recipeImage = response.data.image;
        $(".modal1-img").append(`
            <img src='${recipeImage}'/>
        `);

        $(".modal1-title").append(`
            <h5>${recipeTitle}</h5>
        `);

        $(".modal1-ingredients").append("<h6>Ingredients</h6>")
        for(const ingredient of ingredientList){
            $(".modal1-ingredients").append(`
            <p>${ingredient.original}</p>
            `)
        }
        
        $(".modal1-instructions").append("<h6>Instructions</h6>")
        for(const step of recipeSteps){
            $(".modal1-instructions").append(`
            <p>${step.step}</p>
            `)
        }
        $(".modal1").show();
};


$(".recipe-container").on("click", ".more-info", function(){
    const recipeId = $(this)[0].attributes[0].nodeValue;
    const parentElem = $(this).parent();

    axios.get(`/recipes/get/${recipeId}`)
        .then(function (response) {
            console.log(response);
            recipeModal(response);
        })
        .catch(function (error) {
            parentElem.html("<p>Recipe details not available</p>");
        })
});

$(".recipe-container").on("click", ".remove-recipe", function(){
    const parentElem = $(this).parent();
    const foodId = $(this)[0].dataset.foodId;

    axios.get(`/users/recipes/remove/${foodId}`)
        .then(function (response) {
            if (response.data == "Success"){
                parentElem.html("<p>Recipe Removed!</p>")
            }
        })
        .catch(function (error) {
            parentElem.html("<p>Something Went wrong please try again later</p>")
        })
});

$('.modal1').on("click", ".close", function(){
    $(".modal1").hide();
});

// on load function
$(function() {
    $(".recipes").hide();
});
