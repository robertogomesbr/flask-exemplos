from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

inscritos = []

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    erros = []

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirma_senha = request.form.get('confirma_senha', '')

        if len(nome) < 3:
            erros.append('O nome deve ter pelo menos 3 caracteres.')

        if '@' not in email:
            erros.append('O email deve conter @ para ser válido.')

        if len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')

        if senha != confirma_senha:
            erros.append('A senha e a confirmação de senha devem ser iguais.')

        nascimento_txt = request.form.get('nascimento', '')
        nascimento = None
        idade = None

        try:
            if nascimento_txt:
                nascimento = date.fromisoformat(nascimento_txt)
                hoje = date.today()
                idade = hoje.year - nascimento.year
                if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
                    idade -= 1

                if idade < 16:
                    erros.append('A idade deve ter no mínimo 16 anos.')
            else:
                erros.append('A data de nascimento precisa ser informada.')
        except ValueError:
            erros.append('Informe uma data de nascimento válida.')

        telefone = request.form.get('telefone', '')
        genero = request.form.get('genero', '')
        curso = request.form.get('curso', '')

        periodo_txt = request.form.get('periodo', '')
        periodo = int(periodo_txt) if periodo_txt.isdigit() else None
        if periodo is None or periodo < 1 or periodo > 10:
            erros.append('O período deve ser de 1 a 10.')

        experiencia_txt = request.form.get('experiencia', '0')
        experiencia = int(experiencia_txt) if experiencia_txt.isdigit() else 0

        linguagens = request.form.getlist('linguagens')
        if not linguagens:
            erros.append('Selecione no mínimo 1 linguagem.')

        areas = request.form.getlist('areas')
        github = request.form.get('github', '').strip()
        camiseta = request.form.get('camiseta', '')
        cor_cracha = request.form.get('cor_cracha', '#3b82f6')
        horario_chegada = request.form.get('chegada', '')
        restricao = request.form.get('restricao', '')

        foto = request.files.get('foto')
        nome_foto = ''
        if foto and foto.filename:
            nome_seguro = secure_filename(foto.filename)
            os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
            caminho_foto = os.path.join('static', 'uploads', nome_seguro)
            foto.save(caminho_foto)
            nome_foto = nome_seguro

        motivacao = request.form.get('motivacao', '')
        if len(motivacao) > 500:
            erros.append('A motivação deve ter no máximo 500 caracteres.')

        aceite_regulamento = request.form.get('aceite') == 'on'
        if not aceite_regulamento:
            erros.append('O regulamento deve ser aceito.')

        receber_novidades = request.form.get('newsletter') == 'sim'
        evento_id = request.form.get('evento_id', '')

        dados = {
            'evento_id': evento_id,
            'nome': nome,
            'email': email,
            'data_nascimento': nascimento,
            'idade': idade,
            'telefone': telefone,
            'genero': genero,
            'curso': curso,
            'periodo': periodo,
            'experiencia': experiencia,
            'linguagens': linguagens,
            'areas': areas,
            'github': github,
            'camiseta': camiseta,
            'cor_cracha': cor_cracha,
            'horario_chegada': horario_chegada,
            'restricao': restricao,
            'nome_foto': nome_foto,
            'motivacao': motivacao,
            'aceite_regulamento': aceite_regulamento,
            'receber_novidades': receber_novidades
        }

        if erros:
            return render_template('inscricao.html', erros=erros, form=request.form)

        dados['id'] = len(inscritos) + 1
        inscritos.append(dados)

        return redirect(url_for('confirmacao', id=dados['id']))

    return render_template('inscricao.html', erros=erros, form=request.form)

@app.route('/confirmacao/<int:id>')
def confirmacao(id):
    for inscrito in inscritos:
        if inscrito['id'] == id:
            return render_template('confirmacao.html', dados=inscrito)

    return redirect(url_for('inscricao'))

@app.route('/inscritos')
def listar_inscritos():
    curso = request.args.get('curso', '')
    if curso:
        resultado = [inscrito for inscrito in inscritos if inscrito['curso'] == curso]
    else:
        resultado = inscritos

    return render_template('inscritos.html', inscritos=resultado, curso=curso)

if __name__ == '__main__':
    app.run(debug=True)
