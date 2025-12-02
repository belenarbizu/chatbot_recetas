import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import pickle

def open_file():
    try:
        with open('intentions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print("JSON file loaded successfully.")
            return data
    except FileNotFoundError:
        print("The file intentions.json was not found.")
        return None


def create_dataset(data):
    sentences = []
    labels = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            sentences.append(pattern)
            labels.append(intent['tag'])
    
    print("Dataset created successfully.")
    return sentences, labels


def preprocess_data(sentences, labels):
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X = tfidf_vectorizer.fit_transform(sentences)

    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)

    print("Data preprocessed successfully.")

    return X, y, tfidf_vectorizer, encoder


def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Data split into training and testing sets successfully.")
    return X_train, X_test, y_train, y_test


def create_model(X_train, y_train, X_test, y_test):
    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    print(f"Model created and evaluated successfully. Accuracy: {accuracy * 100:.2f}%")
    return model


def save_model(model, tfidf_vectorizer, encoder):
    with open('model.pkl', 'wb') as file:
        pickle.dump({'model': model, 'vectorizer': tfidf_vectorizer, 'encoder': encoder}, file)
    


def main():
    data = open_file()
    if not data:
        exit(1)
    sentences, labels = create_dataset(data)
    X, y, tfidf_vectorizer, encoder = preprocess_data(sentences, labels)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model = create_model(X_train, y_train, X_test, y_test)
    save_model(model, tfidf_vectorizer, encoder)


if __name__ == "__main__":
    main()