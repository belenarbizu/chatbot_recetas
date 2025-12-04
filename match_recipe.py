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

TYPE_FOOD = {
    "almuerzo": "almuerzo",
    "desayuno": "desayuno",
    "cena": "cena",
    "tapa": "tapa",
    "postre": "postre",
    "comida": "almuerzo",
    "comida principal": "almuerzo",
    "plato principal": "almuerzo",
    "aperitivo": "tapa",
    "comida ligera": "cena",
    "almorzar": "almuerzo",
    "cenar": "cena",
    "tapeo": "tapa",
    "dulce": "postre"
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


def get_type_food_from_text(text):
    text_lower = text.lower()
    for type_food in TYPE_FOOD.keys():
        if type_food in text_lower:
            return TYPE_FOOD[type_food]
    return None


def score_recipe_match(receta, input_ingredients, dieta=None, type_food=None):
    score = 0

    receta_ingredients = receta.get('ingredientes', [])
    matching_ingredients = set(receta_ingredients).intersection(set(input_ingredients))
    score += len(matching_ingredients) * 2

    main_ingredients = receta.get('ingredientes_principales', [])
    matching_main_ingredients = set(main_ingredients).intersection(set(input_ingredients))
    score += len(matching_main_ingredients) * 5

    missing_ingredients = set(main_ingredients) - set(input_ingredients)
    score -= len(missing_ingredients)

    if dieta:
        dieta_type = receta.get('dieta', None)
        if dieta in dieta_type:
            score += 10
    
    if type_food:
        receta_type_food = receta.get('tipo_comida', None)
        if type_food in receta_type_food:
            score += 5

    return score


def find_best_recipes(recetas, input_ingredients, dieta=None, type_food=None):
    scores = []

    for receta in recetas:
        score = score_recipe_match(receta, input_ingredients, dieta, type_food)
        if score > 0:
            scores.append((receta, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    best_recipes = [receta for receta, score in scores[:3]]
    return best_recipes