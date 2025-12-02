import pickle
import json

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


def predict(model, tfidf_vectorizer, encoder, text):
    try:
        with open('intentions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("The file intentions.json was not found.")
        return None
    X_test = tfidf_vectorizer.transform([text])
    y_pred = model.predict(X_test)[0]
    tag = encoder.inverse_transform([y_pred])[0]
    for intent in data['intents']:
        if intent['tag'] == tag:
            return intent['responses']
    return tag


def main():
    model, tfidf_vectorizer, encoder = load_model()
    if not model:
        exit(1)
    user_input = input("Enter your message: ")
    tag = predict(model, tfidf_vectorizer, encoder, user_input)
    if tag:
        print(f"The predicted intent tag is: {tag}")


if __name__ == "__main__":
    main()