import pickle
import json
import random
from match_recipe import get_all_ingredients, get_diet_from_text, get_ingredients_from_text, get_difficulty_from_text, get_time_from_text, find_best_recipes, get_type_food_from_text
from logger import Logger

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


def open_recipes_file():
    try:
        with open('data/recetas.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("The file recetas.json was not found.")
        return None


def predict(model, tfidf_vectorizer, encoder, text):
    data = open_intentions_file()
    if not data:
        exit(1)
    recipes = open_recipes_file()
    if not recipes:
        exit(1)

    X_test = tfidf_vectorizer.transform([text])
    y_pred = model.predict(X_test)[0]
    probabilities = model.predict_proba(X_test)[0]
    max_probability = max(probabilities)
    tag = encoder.inverse_transform([y_pred])[0]

    for intent in data['intents']:
        if tag == "buscar_receta":
            ingredients = get_all_ingredients(recipes)
            text_ingredients = get_ingredients_from_text(text, ingredients)
            type_food = get_type_food_from_text(text)
            difficulty = get_difficulty_from_text(text)
            time = get_time_from_text(text)
            if type_food or difficulty or time:
                best_recipes, best_recipes_info = find_best_recipes(recipes, text_ingredients, type_food=type_food, difficulty=difficulty, time=time)
            else:
                best_recipes, best_recipes_info = find_best_recipes(recipes, text_ingredients)
            if not best_recipes:
                return "No se encontraron recetas que coincidan con los ingredientes proporcionados.", False, max_probability
            recipe = random.choice(best_recipes)
            recipe_info = best_recipes_info[best_recipes.index(recipe)]
            logger.log_interaction(text, recipe, max_probability, recipe_info)
            return recipe, True, max_probability
        if tag == "dietas":
                ingredients = get_all_ingredients(recipes)
                text_ingredients = get_ingredients_from_text(text, ingredients)
                type_food = get_type_food_from_text(text)
                diet = get_diet_from_text(text)
                difficulty = get_difficulty_from_text(text)
                time = get_time_from_text(text)
                if not diet:
                    return "¿Qué tipo de dieta sigues? (vegana, vegetariana, sin gluten)", False, max_probability
                if type_food or difficulty or time:
                    best_recipes, best_recipes_info = find_best_recipes(recipes, text_ingredients, diet, type_food, difficulty, time)
                else:
                    best_recipes, best_recipes_info = find_best_recipes(recipes, text_ingredients, diet)
                if not best_recipes:
                    return f"No se encontraron recipes para la dieta {diet}.", False, max_probability
                recipe = random.choice(best_recipes)
                recipe_info = best_recipes_info[best_recipes.index(recipe)]
                logger.log_interaction(text, recipe, max_probability, recipe_info)
                return recipe, True, max_probability
        if intent['tag'] == tag:
            if len(intent['responses']) > 1:
                respone = random.choice(intent['responses'])
                logger.log_interaction(text, respone, max_probability)
                return respone, False, max_probability
            logger.log_interaction(text, intent['responses'][0], max_probability)
            return intent['responses'][0], False, max_probability
    
    logger.log_interaction(text, "fallback", max_probability)
    return None, 0.0


def main():
    model, tfidf_vectorizer, encoder = load_model()
    if not model:
        exit(1)
    user_input = input("Enter your message: ")
    response, _, _ = predict(model, tfidf_vectorizer, encoder, user_input)
    if response:
        print(f"The predicted response is: {response}")


if __name__ == "__main__":
    main()