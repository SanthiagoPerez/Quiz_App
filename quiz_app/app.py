from flask import Flask, render_template, request, session, redirect, url_for
import json, random, os

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesario para usar sesiones

# Filtro personalizado para convertir índices numéricos en letras
@app.template_filter('chr')
def chr_filter(value):
    return chr(value + 97)  # Convierte 0 -> 'a', 1 -> 'b', etc. 

@app.route('/')  # Página de inicio 
def index():
    return render_template('index.html')

@app.route('/instrucciones', methods=['GET'])  # Página de instrucciones
def instrucciones():
    nombre = request.args.get('nombre')  # Captura el nombre enviado desde el formulario
    return render_template('instrucciones.html', nombre=nombre)

@app.route('/preguntas', methods=['GET', 'POST'])  # Página de preguntas
def quiz():
    if request.method == 'GET':
        # Inicializa las preguntas y la sesión
        if 'preguntas' not in session:  # Solo inicializa si no hay preguntas en la sesión
            filepath = os.path.join(os.path.dirname(__file__), 'questions.json')
            with open(filepath, 'r', encoding='utf-8') as file:  # Especifica la codificación UTF-8
                 questions = json.load(file)
                 selected_questions = random.sample(questions, 10)  # Selecciona 10 preguntas aleatorias
                 session['preguntas'] = selected_questions  # Guarda las preguntas en la sesión
                 session['pregunta_actual'] = 0  # Inicializa el índice de la pregunta actual
                 session['puntuacion'] = 0  # Inicializa la puntuación

    if request.method == 'POST':
        preguntas = session.get('preguntas', [])
        pregunta_actual = session.get('pregunta_actual', 0)

        if pregunta_actual < len(preguntas):
            respuesta = request.form.get('respuesta')  # Captura la respuesta del usuario
            # Compara la respuesta enviada (letra) con la respuesta correcta
            if respuesta == preguntas[pregunta_actual]['respuesta_correcta']:
                session['puntuacion'] += 10  # Suma 10 puntos si la respuesta es correcta
            session['pregunta_actual'] += 1  # Avanza a la siguiente pregunta

        # Redirige después de procesar la respuesta para evitar reenvío de formulario
        return redirect(url_for('quiz'))

    # Pasa la pregunta actual a la plantilla
    preguntas = session.get('preguntas', [])
    pregunta_actual = session.get('pregunta_actual', 0)
    if pregunta_actual < len(preguntas):
        pregunta = preguntas[pregunta_actual]
        return render_template('preguntas.html', pregunta=pregunta, pregunta_actual=pregunta_actual)

    return redirect(url_for('resultado'))  # Redirige a resultados si algo falla

@app.route('/resultado')  # Página de resultados
def resultado():
    puntuacion = session.get('puntuacion', 0)
    return render_template('resultado.html', puntuacion=puntuacion)

@app.route('/reiniciar')  # Ruta para reiniciar el cuestionario
def reiniciar():
    session.clear()  # Limpia todas las variables de sesión
    return redirect(url_for('index'))  # Redirige al inicio

if __name__ == '__main__':
    app.run(debug=True, port=5000)