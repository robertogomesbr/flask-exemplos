from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    nome = None
    if request.method == 'POST':
        nome = request.form.get('nome')
    return render_template('index.html', nome=nome)

@app.route('/users/<nome>')
def usuarios(nome):
    preferencias = ['futebol', 'basquete', 'tenis']
    emailValido = True
    return render_template('users.html', nome=nome, preferencias=preferencias, emailValido=emailValido)

app.run(debug=True)