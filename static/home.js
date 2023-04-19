$(function() {
    axios.get('/users/saved_ingredients')
        .then(function (response) {
            for(ingredient_id of response.data){
            axios.get(`/ingredients/search/${ingredient_id}`)
            .then(function (response) {
                console.log(response)
                $("#ingredient-container").append(`
                    <div class='col-md-4 col-6 my-auto'>
                    <div class='ingredient-card d-flex align-items-center flex-column'>
                    <img src='${response.data.hints[0].food.image || "/static/images/default-ingredient-img.png"}' alt='food image'/>
                    <h6>${response.data.hints[0].food.label}</h6>
                    <i data-food-id ='${response.data.hints[0].food.foodId}' class="btn btn-secondary remove-ingredient mb-3">Remove Ingredient</i>
                    <i class="btn btn-secondary add-to-pot">Add to Pot</i>
                    </div>
                    </div>
                    </div
                    `    
                )
                
            })
            }
            console.log(response)
        })
        .catch(function (error) {
            // handle error
            console.log(error);
        })
});