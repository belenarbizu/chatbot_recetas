import pickle
import json
import random
from match_recipe import get_all_ingredients, get_ingredients_from_text, score_recipe_match, find_best_recipes

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
        if tag == "buscar_receta" or tag == "dieta":
            ingredients = get_all_ingredients(recetas)
            text_ingredients = get_ingredients_from_text(text, ingredients)
            best_recetas = find_best_recipes(recetas, text_ingredients)
            if not best_recetas:
                return "No se encontraron recetas que coincidan con los ingredientes proporcionados.", None, max_probability
            receta = random.choice(best_recetas)
            return receta['nombre'], receta["instrucciones"], max_probability
        if intent['tag'] == tag:
            if isinstance(intent['responses'], list):
                return random.choice(intent['responses']), None, max_probability
            return intent['responses'], None, max_probability
    return None, None, 0.0


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