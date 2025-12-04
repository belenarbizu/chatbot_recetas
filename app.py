import gradio as gr
import pickle
from chatbot_predict import predict
import json
import random

THRESHOLD = 0.45

def main():
    try:
        with open('model.pkl', 'rb') as file:
            data = pickle.load(file)
            model = data['model']
            tfidf_vectorizer = data['vectorizer']
            encoder = data['encoder']
    except Exception as e:
        print(f"Error loading the model: {e}")
        return

    def chatbot_response(user_input, history):
        response, ingredients, instructions, probability = predict(model, tfidf_vectorizer, encoder, user_input)

        if probability < THRESHOLD:
            return ["No estoy seguro de entenderte. ¿Podrías reformular tu pregunta sobre recetas de comida?"]

        if isinstance(response, list):
            response = random.choice(response)

        if instructions and ingredients:
            return [f"Receta: {response}\nIngredientes: {', '.join(ingredients)}\nInstrucciones: {instructions}"]
        else:
            return response

    gr.ChatInterface(chatbot_response, title="Chatbot Intent Predictor").launch()


if __name__ == "__main__":
    main()