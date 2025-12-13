import gradio as gr
import pickle
from chatbot_predict import predict
import json
import random
from logger import Logger
import os
from context import Context

THRESHOLD = 0.45

def main():
    logger = Logger()
    context = Context()

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
        nonlocal context
        try:
            response, is_a_recipe, probability, updated_context = predict(model, tfidf_vectorizer, encoder, user_input, context)
        except Exception as e:
            print(f"Error: {e}")
            return "Lo siento, ha ocurrido un error al procesar tu solicitud. Por favor, intenta de nuevo."
        context = updated_context

        if probability < THRESHOLD:
            return ["No estoy seguro de entenderte. ¿Podrías reformular tu pregunta sobre recetas de comida?"]

        if isinstance(response, list):
            response = random.choice(response)

        if is_a_recipe:
            phrase = f"¡Te sugiero {response['nombre']}!"

            reasons = []
            if context.user_ingredients:
                reasons.append(f"porque coincide con los ingredientes que tienes: {', '.join(context.user_ingredients)}")
            if context.diet:
                reasons.append(f"porque es apta para la dieta {context.diet}")
            if context.type_food:
                reasons.append(f"porque es para una {context.type_food}")
            if context.difficulty:
                reasons.append(f"porque tiene una dificultad {context.difficulty}")
            if context.time:
                reasons.append(f"porque se puede preparar en {context.time} minutos o menos")
            
            if reasons:
                phrase += f"\n\nTe la recomiendo {', '.join(reasons)}."

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
            return stats_text
        else:
            return "No se pudieron obtener las estadísticas."


    def reset_context():
        nonlocal context
        context.reset()
        return "Conversación reiniciada."


    def show_context():
        nonlocal context
        summary = context.get_context_summary()
        context_text = "Contexto actual:\n"
        context_text += f"Ingredientes: {', '.join(summary['ingredients']) if summary['ingredients'] else 'Ninguno'}\n"
        context_text += f"Dieta: {summary['diet'] if summary['diet'] else 'Ninguna'}\n"
        context_text += f"Tipo de comida: {summary['type_food'] if summary['type_food'] else 'Ninguno'}\n"
        context_text += f"Dificultad: {summary['difficulty'] if summary['difficulty'] else 'Ninguna'}\n"
        context_text += f"Tiempo: {summary['time'] if summary['time'] else 'Ninguno'} minutos\n"
        context_text += f"Últimas recetas sugeridas: {len(summary['last_recipes'])}\n"
        return context_text


    with gr.Blocks() as demo:
        gr.Markdown("# Chatbot Intent Predictor")
        gr.Markdown("""
        ### ¿Cómo usar este chatbot?
        1. Dime qué ingredientes tienes disponibles: "Tengo huevos y patatas".
        2. Añade preferencias (opcional): "Algo vegano para cenar", "Quiero una receta rápida".
        3. Elige entre las opciones que te sugiero.

        **Tip**: Puedo recordar ingredientes y preferencias que me digas durante la conversación. Si dices "también tengo espinacas y queso", buscaré recetas que incluyan todos esos ingredientes.
        """)

        chatbot = gr.Chatbot(height=500)

        gr.ChatInterface(
            chatbot_response,
            chatbot=chatbot,
            examples=[
                "Tengo huevos y patatas",
                "También tengo espinacas y queso",
                "Quiero algo vegano para cenar",
                "Dame una receta fácil y rápida",
                "Algo con pollo sin gluten"
            ])

        with gr.Row():
            stats_button = gr.Button("Ver estadísticas de interacciones", size="sm")
            reset_button = gr.Button("Reiniciar conversación", size="sm")
            context_button = gr.Button("Ver contexto actual", size="sm")
        
        info_output = gr.Textbox(label="Información", lines=4)

        stats_button.click(fn=show_statistics, inputs=None, outputs=info_output)
        reset_button.click(fn=reset_context, inputs=None, outputs=info_output)
        context_button.click(fn=show_context, inputs=None, outputs=info_output)

    demo.launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()