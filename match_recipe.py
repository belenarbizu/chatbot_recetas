DIETA = {
    "vegana": "vegano",
    "vegano": "vegano",
    "vegetariana": "vegetariano",
    "vegetariano": "vegetariano",
    "sin gluten": "sin_gluten",
    "no gluten": "sin_gluten",
    "no tolero el gluten": "sin_gluten",
    "no como gluten": "sin_gluten",
    "no como carne": "vegetariano",
    "no como pescado": "vegetariano",
    "no como marisco": "vegetariano",
    "sin carne": "vegetariano",
    "sin pescado": "vegetariano",
    "sin marisco": "vegetariano"
}

def get_all_ingredients(recetas):
    ingredients_set = set()
    for receta in recetas:
        for ingrediente in receta.get('ingredientes', []):
            ingredients_set.add(ingrediente)
    return list(ingredients_set)


def get_ingredients_from_text(text, ingredients):
    found_ingredients = set()
    text_lower = text.lower()
    for ingredient in ingredients:
        if ingredient.lower() in text_lower:
            found_ingredients.add(ingredient)
    return list(found_ingredients)


def score_recipe_match(receta, input_ingredients, dieta=None):
    score = 0

    receta_ingredients = receta.get('ingredientes', [])
    matching_ingredients = set(receta_ingredients).intersection(set(input_ingredients))
    score += len(matching_ingredients)

    main_ingredients = receta.get('ingredientes_principales', [])
    matching_main_ingredients = set(main_ingredients).intersection(set(input_ingredients))
    score += len(matching_main_ingredients) * 5

    #missing ingredients??

    if dieta:
        dieta_type = receta.get('dieta', None)
        if dieta in dieta_type:
            score += 10

    return score


def find_best_recipes(recetas, input_ingredients, dieta=None):
    scores = []

    for receta in recetas:
        score = score_recipe_match(receta, input_ingredients, dieta)
        if score > 0:
            scores.append((receta, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    best_recipes = [receta for receta, score in scores[:3]]
    return best_recipes