$(function() {
    axios.get('/users/saved_recipes')
    .then(function (response) {
        for(recipe_id of response.data){ 
            axios.get(`/recipes/get/${recipe_id}`)
            .then(function (response) {
                console.log(response)
                $(".recipe-container").append(`
                    <div class='col-lg-3 col-md-4 col-6 my-auto'>
                    <div class='recipe-card'>
                    <img src='${response.data.image || "/static/images/default-ingredient-img.png"}' alt='food image'/>
                    <h6>${response.data.title}</h6>
                    <i data-food-id ='${response.data.id}' class="btn btn-secondary remove-recipe">Remove Recipe</i>
                    <i data-food-id ='${response.data.id}' class="btn btn-secondary more-info">More Info</i>
                    </div>
                    </div
                `
            )
        })
        }
    })
    .catch(function (error) {
        // handle error
        console.log(error);
    })
});