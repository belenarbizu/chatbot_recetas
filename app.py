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
        response, is_a_recipe, probability = predict(model, tfidf_vectorizer, encoder, user_input)

        if probability < THRESHOLD:
            return ["No estoy seguro de entenderte. ¿Podrías reformular tu pregunta sobre recetas de comida?"]

        if isinstance(response, list):
            response = random.choice(response)

        if is_a_recipe:
            phrase = f"¡Te sugiero {response['nombre']}!"
            phrase += f"\n\n📝 Ingredientes:\n" + "\n".join([f"• {ing}" for ing in response['ingredientes']])
            phrase += f"\n\n📌 Instrucciones:\n" + f"{response['instrucciones']}"
            phrase += f"\n\n📊 Información:"
            phrase += f"\n• Porciones: {response['porciones']}"
            phrase += f"\n• Tiempo: {response['tiempo_minutos']} minutos"
            phrase += f"\n• Dificultad: {response['dificultad'].capitalize()}"
            phrase += f"\n• Calorías aprox: {response['calorias_aprox']} kcal/porción"
            if response.get('dieta'):
                phrase += f"\n• Dieta: {', '.join(response['dieta'])}"
            return phrase
        else:
            return response

    chatbot = gr.Chatbot(height=600)

    gr.ChatInterface(
        chatbot_response,
        chatbot=chatbot,
        title="Chatbot Intent Predictor",
        description="Dime qué ingredientes tienes y te sugiero recetas. También puedes filtrar por dieta, dificultad o tiempo de preparación.",
        examples=[
            "Tengo huevos y patatas",
            "Quiero algo vegano para cenar",
            "Dame una receta fácil y rápida",
            "Algo con pollo sin gluten"
        ]).launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()