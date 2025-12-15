import pickle
import json
import random
from match_recipe import (
    get_diet_from_text,
    get_ingredients_from_text,
    get_difficulty_from_text,
    get_time_from_text,
    find_best_recipes,
    get_type_food_from_text
)
from logger import Logger
from context import Context
from recipe_cache import get_recipes_cached, get_all_ingredients_cached

logger = Logger()


def load_model():
    try:
        with open('model.pkl', 'rb') as file:
            data = pickle.load(file)
            model = data['model']
            tfidf_vectorizer = data['vectorizer']
            encoder = data['encoder']
            print("Model loaded successfully.")
            return model, tfidf_vectorizer, encoder
    except FileNotFoundError:
        print("The model file was not found.")
        return None, None, 


def open_intentions_file():
    try:
        with open('data/intentions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("The file intentions.json was not found.")
        return None


# def open_recipes_file():
#     try:
#         with open('data/recetas.json', 'r', encoding='utf-8') as file:
#             data = json.load(file)
#             return data
#     except FileNotFoundError:
#         print("The file recetas.json was not found.")
#         return None


def get_info_from_user_input(text, ingredients):
    ingredients = get_ingredients_from_text(text, ingredients)
    type_food = get_type_food_from_text(text)
    difficulty = get_difficulty_from_text(text)
    time = get_time_from_text(text)
    diet = get_diet_from_text(text)
    return ingredients, type_food, difficulty, time, diet


def predict(model, tfidf_vectorizer, encoder, text, context=None):
    data = open_intentions_file()
    recipes = get_recipes_cached()
    if not data or not recipes:
        exit(1)
    
    if context is None:
        context = Context()
    
    if context.is_expired():
        context.reset()

    X_test = tfidf_vectorizer.transform([text])
    y_pred = model.predict(X_test)[0]
    probabilities = model.predict_proba(X_test)[0]
    max_probability = max(probabilities)
    tag = encoder.inverse_transform([y_pred])[0]

    if context and context.last_intent == "multiple_options":
        selection_idx = None
        if "primera" in text.lower() or "primero" in text.lower() or "1" in text.lower() or "uno" in text.lower():
            selection_idx = 0
        elif "segunda" in text.lower() or "segundo" in text.lower() or "2" in text.lower() or "dos" in text.lower():
            selection_idx = 1
        elif "tercera" in text.lower() or "tercero" in text.lower() or "3" in text.lower() or "tres" in text.lower():
            selection_idx = 2
        
        if selection_idx is None:
            text_lower = text.lower()
            for idx, recipe in enumerate(context.last_recipes):
                if recipe['nombre'].lower() in text_lower:
                    selection_idx = idx
                    break
        
        if selection_idx is not None and selection_idx < len(context.last_recipes):
            recipe = context.last_recipes[selection_idx]
            logger.log_interaction(text, recipe, max_probability)
            context.set_last_intent(None)
            return recipe, True, 1.0, context

    for intent in data['intents']:
        if tag == "buscar_receta":
            ingredients = get_all_ingredients_cached()
            text_ingredients, type_food, difficulty, time, diet = get_info_from_user_input(text, ingredients)
            if text_ingredients:
                context.add_ingredients(text_ingredients)
            if diet:
                context.set_diet(diet)
            if type_food:
                context.set_type_food(type_food)
            if difficulty:
                context.set_difficulty(difficulty)
            if time:
                context.set_time(time)
            if context.user_ingredients:
                best_recipes, best_recipes_info = find_best_recipes(recipes, context.user_ingredients, diet=context.diet, type_food=context.type_food, difficulty=context.difficulty, time=context.time)
            else:
                best_recipes, best_recipes_info = find_best_recipes(recipes, text_ingredients, diet=diet, type_food=type_food, difficulty=difficulty, time=time)
            if not best_recipes:
                return "No se encontraron recetas que coincidan con los datos dados.", False, max_probability, context
            if len(best_recipes) > 1:
                context.set_last_intent("multiple_options")
                context.add_recipes(best_recipes)
                respone = "He encontrado varias recetas que podrían interesarte:\n"
                for idx, recipe in enumerate(best_recipes):
                    respone += f"{idx+1}. {recipe['nombre']}\n"
                respone += "\n Dime el número o el nombre de la receta que te gustaría conocer."
                logger.log_interaction(text, respone, max_probability)
                return respone, False, max_probability, context
            else:
                recipe = random.choice(best_recipes)
                recipe_info = best_recipes_info[best_recipes.index(recipe)]
                logger.log_interaction(text, recipe, max_probability, recipe_info)
                return recipe, True, max_probability, context
        if intent['tag'] == tag:
            if len(intent['responses']) > 1:
                respone = random.choice(intent['responses'])
                logger.log_interaction(text, respone, max_probability)
                return respone, False, max_probability, context
            logger.log_interaction(text, intent['responses'][0], max_probability)
            return intent['responses'][0], False, max_probability, context
    
    logger.log_interaction(text, "fallback", max_probability)
    return None, False, 0.0, context


def main():
    model, tfidf_vectorizer, encoder = load_model()
    if not model:
        exit(1)
    user_input = input("Enter your message: ")
    response, _, _, _ = predict(model, tfidf_vectorizer, encoder, user_input)
    if response:
        print(f"The predicted response is: {response}")


if __name__ == "__main__":
    main()