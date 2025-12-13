---
title: Chatbot de Recetas con NLP
emoji: 🍳
colorFrom: orange
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# 🍳 Asistente de Recetas con IA

Un chatbot inteligente que te sugiere recetas basándose en tus ingredientes disponibles.

## ✨ Características

- 🥘 **Búsqueda por ingredientes**: Dile qué tienes en la nevera
- 🔍 **Filtros inteligentes**: Vegano, sin gluten, fácil, rápido...
- 🧠 **Contexto conversacional**: Recuerda ingredientes durante la conversación
- 📊 **30 recetas españolas** incluidas

## 🚀 Cómo usar

1. Dile al bot qué ingredientes tienes
2. Añade preferencias (opcional): vegano, fácil, rápido...
3. Elige entre las opciones sugeridas

## 🛠️ Tecnologías

- **NLP**: TF-IDF + SVM para clasificación de intenciones
- **Interfaz**: Gradio
- **Matching**: Normalización de texto y scoring de recetas

## 📝 Ejemplos
```
Usuario: "Tengo huevos y patatas"
Bot: Sugiere Tortilla de patatas

Usuario: "También tengo cebolla"
Bot: Busca con todos los ingredientes acumulados
```

## 👨‍💻 Autor

[Belén Arbizu] - [belenarbizu]
```

### C) **Estructura de archivos para HF**
```
tu-chatbot-recetas/
│
├── app.py                    # Punto de entrada
├── chatbot_predict.py
├── logger.py
├── context.py
├── match_recipe.py
├── chatbot_train.py
├── filters.py
│
├── data/
│   ├── intentions.json
│   └── recetas.json
│
├── model.pkl                 # Modelo entrenado
│
├── requirements.txt
├── README.md
└── .gitignore
```
