from flask import Flask, render_template, request, session, redirect, url_for
import json, random, os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# el chr nos permite convertir los indices en las letras
# en este caso a, b, c, d
@app.template_filter('chr')
def chr_filter(value):
    return chr(value + 97) 

# Ruta para la página de inicio
@app.route('/')  
def index():
    return render_template('index.html')

# Ruta para la página de instrucciones
@app.route('/instrucciones', methods=['POST'])  
def instrucciones():
    nombre = request.form.get('nombre')    
    if nombre:
        session['usuario'] = nombre     
    return render_template('instrucciones.html', nombre=nombre)

# Ruta para la pagina de las preguntas
# selected_questions = random.sample(questions, 10) -> estamos seleccionando 10 preguntas aleatorias
@app.route('/preguntas', methods=['GET', 'POST']) 
def quiz():
    if request.method == 'GET':
        if 'preguntas' not in session:  
            filepath = os.path.join(os.path.dirname(__file__), 'questions.json')
            with open(filepath, 'r', encoding='utf-8') as file:
                 questions = json.load(file)
                 selected_questions = random.sample(questions, 10)
                 session['preguntas'] = selected_questions
                 session['pregunta_actual'] = 0
                 session['puntuacion'] = 0
                 session['resultados_preguntas'] = []

    if request.method == 'POST':
        preguntas = session.get('preguntas', [])
        pregunta_actual = session.get('pregunta_actual', 0)
        resultados_preguntas = session.get('resultados_preguntas', [])

        if pregunta_actual < len(preguntas):
            pregunta_obj = preguntas[pregunta_actual]
            
            # Obtener respuestas del usuario
            if pregunta_obj.get('tipo') == 'multiple':
                # Para preguntas múltiples, buscar todas las respuestas marcadas
                respuestas_usuario = []
                for i in range(len(pregunta_obj['opciones'])):
                    respuesta_key = f'respuesta_{i}'
                    if request.form.get(respuesta_key):
                        respuestas_usuario.append(request.form.get(respuesta_key))
                
                respuestas_correctas = pregunta_obj['respuesta_correcta']
                
                # Calcular puntaje proporcional
                correctas_marcadas = set(respuestas_usuario) & set(respuestas_correctas)
                incorrectas_marcadas = set(respuestas_usuario) - set(respuestas_correctas)
                
                # Puntaje = (correctas marcadas - incorrectas) / total correctas * 10
                puntaje_base = len(correctas_marcadas) - len(incorrectas_marcadas)
                puntaje_obtenido = max(0, (puntaje_base / len(respuestas_correctas)) * 10)
                puntaje_obtenido = round(puntaje_obtenido)  # Sin decimales
                
                es_correcta = len(correctas_marcadas) == len(respuestas_correctas) and len(incorrectas_marcadas) == 0
                
            else:  # Pregunta simple
                respuesta_usuario = request.form.get('respuesta')
                es_correcta = respuesta_usuario == pregunta_obj['respuesta_correcta']
                puntaje_obtenido = 10 if es_correcta else 0
            
            # Guardar el resultado
            resultado = {
                'pregunta': pregunta_obj['pregunta'],
                'correcta': es_correcta,
                'puntaje': puntaje_obtenido,
                'puntaje_maximo': 10
            }
            resultados_preguntas.append(resultado)
            
            # Actualizar sesión
            session['resultados_preguntas'] = resultados_preguntas
            session['puntuacion'] += puntaje_obtenido
            session['pregunta_actual'] += 1

        return redirect(url_for('quiz'))
    
    preguntas = session.get('preguntas', [])
    pregunta_actual = session.get('pregunta_actual', 0)
    if pregunta_actual < len(preguntas):
        pregunta = preguntas[pregunta_actual]
        return render_template('preguntas.html', pregunta=pregunta, pregunta_actual=pregunta_actual)
    return redirect(url_for('resultado'))

# Ruta para la página de resultados
@app.route('/resultado')
def resultado():
    puntuacion = session.get('puntuacion', 0)
    nombre = session.get('usuario', 'Usuario Anónimo') 
    resultados_preguntas = session.get('resultados_preguntas', [])
    total_preguntas = len(resultados_preguntas) if resultados_preguntas else 10
    
    return render_template(
        'resultado.html',
        puntuacion=puntuacion,
        usuario=nombre,
        resultados_preguntas=resultados_preguntas,
        total_preguntas=total_preguntas
    )

# Ruta para reiniciar el cuestionario
@app.route('/reiniciar')
def reiniciar():
    session.clear()
    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=False, port=5000)