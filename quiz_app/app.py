from flask import Flask, render_template

app=Flask(__name__)

@app.route('/') # Define la ruta para la página de inicio(raíz)
def index():
    return render_template('index.html') # Renderiza el template index.html

if __name__ == '__main__':
    app.run(debug=True, port=5000)