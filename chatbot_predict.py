import pickle
import json
import random
from match_recipe import get_all_ingredients, get_ingredients_from_text, score_recipe_match, find_best_recipes, DIETA, get_type_food_from_text



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


def open_recetas_file():
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
    recetas = open_recetas_file()
    if not recetas:
        exit(1)

    X_test = tfidf_vectorizer.transform([text])
    y_pred = model.predict(X_test)[0]
    probabilities = model.predict_proba(X_test)[0]
    max_probability = max(probabilities)
    tag = encoder.inverse_transform([y_pred])[0]

    for intent in data['intents']:
        if tag == "buscar_receta":
            ingredients = get_all_ingredients(recetas)
            text_ingredients = get_ingredients_from_text(text, ingredients)
            type_food = get_type_food_from_text(text)
            if type_food:
                best_receipts = find_best_recipes(recetas, text_ingredients, type_food=type_food)
            else:
                best_receipts = find_best_recipes(recetas, text_ingredients)
            if not best_receipts:
                return "No se encontraron recetas que coincidan con los ingredientes proporcionados.", None, None, max_probability
            receta = random.choice(best_receipts)
            return receta['nombre'], receta["ingredientes"], receta["instrucciones"], max_probability
        if tag == "dietas":
            dieta = None
            for word in DIETA.keys():
                if word in text.lower():
                    dieta = DIETA[word]
                    break
            if dieta:
                ingredients = get_all_ingredients(recetas)
                text_ingredients = get_ingredients_from_text(text, ingredients)
                type_food = get_type_food_from_text(text)
                if type_food:
                    best_receipts = find_best_recipes(recetas, text_ingredients, dieta, type_food)
                else:
                    best_receipts = find_best_recipes(recetas, text_ingredients, dieta)
                if not best_receipts:
                    return f"No se encontraron recetas para la dieta {dieta}.", None,None, max_probability
                receta = random.choice(best_receipts)
                return receta['nombre'], receta["ingredientes"], receta["instrucciones"], max_probability
            return "¿Qué tipo de dieta sigues? (vegana, vegetariana, sin gluten)", None, max_probability
        if intent['tag'] == tag:
            if isinstance(intent['responses'], list) and len(intent['responses']) > 1:
                return random.choice(intent['responses']), None, None, max_probability
            return intent['responses'], None, None, max_probability
    return None, None, None, 0.0


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