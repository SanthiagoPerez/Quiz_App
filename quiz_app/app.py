from flask import Flask, render_template
import json, random, os

app=Flask(__name__)

@app.route('/') # Define la ruta para la página de inicio(raíz)
def index():
    return render_template('index.html') # Renderiza el template index.html

@app.route('/preguntas')  # Define la ruta para la página del cuestionario
def quiz():
    filepath = os.path.join(os.path.dirname(__file__), 'questions.json')  
    with open(filepath, 'r') as file:  
        questions = json.load(file)  
        selected_questions = random.sample(questions, 10)  
        for question in selected_questions:  
            random.shuffle(question['opciones'])  
    return render_template('preguntas.html', questions=selected_questions) 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
