from filters import DIET, TYPE_FOOD, DIFFICULTY, TIME

def get_all_ingredients(recipes):
    ingredients_set = set()
    for recipe in recipes:
        for ingrediente in recipe.get('ingredientes', []):
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


def get_diet_from_text(text):
    text_lower = text.lower()
    for diet in DIET.keys():
        if diet in text_lower:
            return DIET[diet]
    return None


def get_difficulty_from_text(text):
    text_lower = text.lower()
    for difficulty in DIFFICULTY.keys():
        if difficulty in text_lower:
            return DIFFICULTY[difficulty]
    return None


def get_time_from_text(text):
    text_lower = text.lower()
    for time_word in TIME.keys():
        if time_word in text_lower:
            return TIME[time_word]
    return None


def score_recipe_match(recipe, input_ingredients, diet=None, type_food=None, difficulty=None, time=None):
    score = 0

    if input_ingredients:
        recipe_ingredients = recipe.get('ingredientes', [])
        matching_ingredients = set(recipe_ingredients).intersection(set(input_ingredients))
        score += len(matching_ingredients) * 2

        main_ingredients = recipe.get('ingredientes_principales', [])
        matching_main_ingredients = set(main_ingredients).intersection(set(input_ingredients))
        score += len(matching_main_ingredients) * 5

        missing_ingredients = set(main_ingredients) - set(input_ingredients)
        score -= len(missing_ingredients)

    if diet:
        dieta_type = recipe.get('dieta', None)
        if diet in dieta_type:
            score += 10
    
    if type_food:
        recipe_type_food = recipe.get('tipo_comida', None)
        if type_food in recipe_type_food:
            score += 5

    if difficulty:
        difficulty_recipe = recipe.get('dificultad', None)
        if difficulty == difficulty_recipe:
            score += 3

    if time:
        time_recipe = recipe.get('tiempo_minutos', None)
        if time_recipe and time_recipe <= time:
            score += 2

    return score


def find_best_recipes(recipes, input_ingredients, diet=None, type_food=None, difficulty=None, time=None):
    scores = []

    for recipe in recipes:
        score = score_recipe_match(recipe, input_ingredients, diet, type_food, difficulty, time)
        if score > 0:
            scores.append((recipe, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    best_recipes = [recipe for recipe, score in scores[:3]]
    return best_recipes