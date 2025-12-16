import gradio as gr
import pickle
from chatbot_predict import predict
import random
from context import Context

THRESHOLD = 0.45

custom_css = """
.avatar-container img {
    width: 40px !important;
    height: 40px !important;
}

.avatar-container {
    width: 40px !important;
    height: 40px !important;
}
"""

def main():
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


    def join_reasons(reasons):
        if len(reasons) == 1:
            return reasons[0]
        elif len(reasons) == 2:
            return ' y '.join(reasons)
        else:
            return ', '.join(reasons[:-1]) + ' y ' + reasons[-1]
    

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
                matching_ingredients = [ing for ing in response['ingredientes'] if ing in context.user_ingredients]
                if matching_ingredients:
                    reasons.append(f"porque coincide con los ingredientes que tienes: {join_reasons(matching_ingredients)}")
            if context.diet:
                reasons.append(f"porque es apta para la dieta {context.diet}")
            if context.type_food:
                reasons.append(f"porque es para una {context.type_food}")
            if context.difficulty:
                reasons.append(f"porque tiene una dificultad {context.difficulty}")
            if context.time:
                reasons.append(f"porque se puede preparar en {context.time} minutos o menos")
            
            if reasons:
                phrase += f"\n\nTe la recomiendo {join_reasons(reasons)}."
    
            phrase += f"\n\n📝 Ingredientes:\n" + ", ".join([f"{ing}" for ing in response['ingredientes']])
            phrase += f"\n\n📌 Instrucciones:\n" + f"{response['instrucciones']}"
            phrase += f"\n\n📊 Información:"
            phrase += f"\n• Porciones: {response['porciones']}"
            phrase += f"\n• Tiempo: {response['tiempo_minutos']} minutos"
            phrase += f"\n• Dificultad: {response['dificultad'].capitalize()}"
            if response.get('dieta'):
                phrase += f"\n• Dieta: {join_reasons(response['dieta'])}"
            return phrase
        else:
            return response


    def reset_context():
        nonlocal context
        context.reset()
        return [], []


    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(height=500, avatar_images=[None, "chatbot_avatar.jpg"])
        
        gr.Markdown("<h1 style='text-align: center; font-size: 22px;'>🍳 Chatbot de Recetas</h1>")

        chat = gr.ChatInterface(
            chatbot_response,
            chatbot=chatbot,
            title=None,
            description="""<div style='font-size: 14px;'>
            ¿Cómo usar este chatbot?</br>
            1. Dime qué ingredientes tienes disponibles: "Tengo huevos y patatas".</br>
            2. Añade preferencias (opcional): "Algo vegano para cenar", "Quiero una receta rápida".</br>
            3. Elige entre las opciones que te sugiero.</br>
            💡<strong>Tip</strong>: Puedo recordar ingredientes y preferencias que me digas durante la conversación. Si dices "también tengo espinacas y queso", buscaré recetas que incluyan todos esos ingredientes.
            </div>""",
            examples=[
                "Tengo huevos y patatas",
                "También tengo espinacas y queso",
                "Quiero algo vegano para cenar",
                "Dame una receta fácil y rápida",
                "Algo con pollo sin gluten"
            ])

        with gr.Row():
            reset_button = gr.Button("Reiniciar conversación", size="sm")

        reset_button.click(fn=reset_context, inputs=None, outputs=[chatbot, chat.chatbot_state])

    demo.launch(theme=gr.themes.Soft(), css=custom_css)


if __name__ == "__main__":
    main()