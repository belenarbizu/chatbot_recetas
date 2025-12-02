import gradio as gr
import pickle
from chatbot_predict import predict
import json

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
        tag = predict(model, tfidf_vectorizer, encoder, user_input)
        return tag

    gr.ChatInterface(chatbot_response, title="Chatbot Intent Predictor").launch()


if __name__ == "__main__":
    main()