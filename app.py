import gradio as gr
import pickle
from chatbot_predict import predict
import json
import random
from logger import Logger
import os

THRESHOLD = 0.45

def main():
    logger = Logger()

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


    def show_statistics():
        stats = logger.get_statistics()
        if stats:
            stats_text = f"Total de interacciones: {stats['total_interactions']}\n"
            stats_text += f"Confianza promedio: {stats['avg_confidence']:.2f}\n"
            stats_text += "Ingredientes más buscados:\n"
            for ingredient, count in sorted(stats['most_searched_ingredients'].items(), key=lambda x: x[1], reverse=True):
                stats_text += f"{ingredient}: {count}\n"
            stats_text += "Dietas más buscadas:\n"
            for diet, count in sorted(stats['most_searched_diets'].items(), key=lambda x: x[1], reverse=True):
                stats_text += f"{diet}: {count}\n"
            return gr.update(value=stats_text)
        else:
            return gr.update(value="No se pudieron obtener las estadísticas.")


    with gr.Blocks() as demo:
        gr.Markdown("# Chatbot Intent Predictor")
        gr.Markdown("Dime qué ingredientes tienes y te sugiero recetas. También puedes filtrar por dieta, dificultad o tiempo de preparación.")

        chatbot = gr.Chatbot(height=500)

        gr.ChatInterface(
            chatbot_response,
            chatbot=chatbot,
            examples=[
                "Tengo huevos y patatas",
                "Quiero algo vegano para cenar",
                "Dame una receta fácil y rápida",
                "Algo con pollo sin gluten"
            ])

        with gr.Row():
            stats_button = gr.Button("Ver estadísticas de interacciones", size="sm")
        
        stats_output = gr.Textbox(label="Estadísticas", lines=4)

        stats_button.click(fn=show_statistics, inputs=None, outputs=stats_output)

    demo.launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()