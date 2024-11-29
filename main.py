from flask import Flask, render_template, request, redirect, flash, url_for, session, make_response, jsonify
from config.db import conexao_db, fechar_conexao
from usuario import Usuario
from werkzeug.security import check_password_hash
from config.secret_key import Secret_key
from noticias import Noticias, salvar_noticias_db, buscar_noticias_db, buscar_por_categoria
from comentario import Comentario
from criptomoedas import Criptomoedas

app = Flask(__name__)

app.config['SECRET_KEY'] = Secret_key.sessao()

@app.route('/teste_conexao')
def teste_conexao():
    conexao = conexao_db()
    if conexao:
        fechar_conexao(conexao)
        return "Conexão com o banco de dados foi bem-sucedida!"
    else:
        return "Erro ao conectar ao banco de dados."

from flask import redirect, url_for

@app.route('/login', methods=['GET', 'POST'])
def login():  
    mensagem = None
    sucesso = None  

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')

        if not email or not senha:
            mensagem = "Por favor, preencha todos os campos."
            sucesso = False
        else:
            usuario_classe = Usuario()
            usuario = usuario_classe.login(email)

            if usuario and check_password_hash(usuario[3], senha): 
                session['email'] = email
                session['usuario_id'] = int(usuario[0])  # Armazena como inteiro
                mensagem = "Login realizado com sucesso!"
                sucesso = True
                # Redireciona para a rota associada ao index.html
                return redirect(url_for('index'))  
            else:
                mensagem = "E-mail ou senha incorretos."
                sucesso = False

    return render_template('login.html', mensagem=mensagem, sucesso=sucesso)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    mensagem = None  # Inicializa como None para não exibir mensagem por padrão

    if request.method == 'POST':  # Somente processa o formulário após o envio
        nome = request.form.get('username')
        email = request.form.get('email')
        senha = request.form.get('password')

        # Valida se os campos foram preenchidos
        if not nome or not email or not senha:
            mensagem = "Por favor, preencha todos os campos."
        else:
            novo_usuario = Usuario(nome, email, senha)
            resultado = novo_usuario.cadastrar_usuario()

            # Lógica para exibir mensagens com base no retorno do método
            if resultado == "O e-mail já está cadastrado. Tente outro.":
                mensagem = resultado
            elif resultado == "Usuário cadastrado com sucesso!":
                return redirect(url_for('login'))  # Redireciona para a página de login
            else:
                mensagem = resultado  # Mensagem genérica de erro retornada pela classe

    return render_template('login.html', mensagem=mensagem)

@app.route('/index')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    noticias_classe = Noticias()
    noticias = noticias_classe.buscar_noticias()

    if noticias:
        salvar_noticias_db(noticias)

    noticias_do_banco = buscar_noticias_db()

    for noticia in noticias_do_banco:
        if 'id' in noticia:
            noticia['comentarios_count'] = Comentario.contar_comentarios(noticia['id'])
        else:
            print("Noticia ID não encontrado")
            noticia['comentarios_count'] = 0

    email = session.get('email', None)

    response = make_response(render_template('index.html',
                                             email=email, 
                                             articles=noticias_do_banco))
    return response

@app.route('/noticias_categoria', methods=['GET'])
def noticias_categoria():
    if 'email' not in session:
        return redirect(url_for('login'))
    categoria = request.args.get('categoria') 

    if not categoria:
        return redirect(url_for('index'))
    noticias_do_banco = buscar_por_categoria(categoria)

    return render_template('index.html',
                           articles=noticias_do_banco,
                           categoria=categoria)


@app.route('/discutir/<int:noticia_id>')
def discutir(noticia_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    conn = conexao_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias WHERE id = %s", (noticia_id,))
    noticia = cursor.fetchone()

    comentarios = Comentario.obter_comentarios(noticia_id)
    print("Comentários retornados:", comentarios)  # Depuração

    cursor.close()
    fechar_conexao(conn)
    
    if noticia:
        return render_template('discutir.html', noticia=noticia, comentarios=comentarios, noticia_id=noticia_id)
    else:
        flash("Notícia não encontrada", "erro")
        return redirect(url_for('index'))


@app.route('/comentarios/<int:noticia_id>', methods=['GET', 'POST'])
def comentario(noticia_id):
    if request.method == 'POST':

        if 'email' not in session:
            flash('Você precisa estar logado para enviar um comentário.', 'erro')
            return redirect(url_for('login'))

        usuario_classe = Usuario(None, session['email'], None)
        usuario = usuario_classe.login(session['email'])
        
        if not usuario:
            flash('Usuário não encontrado.', 'erro')
            return redirect(url_for('login'))

        conteudo = request.form.get('comentario')

        if not conteudo or conteudo.strip() == '':
            flash('O comentário não pode estar vazio.', 'erro')
            return redirect(url_for('discutir', noticia_id=noticia_id))

        novo_comentario = Comentario(conteudo, usuario[0], noticia_id)
        if novo_comentario.inserir_comentario():
            flash('Comentário enviado com sucesso!', 'sucesso')
        else:
            flash('Erro ao enviar comentário.', 'erro')

        return redirect(url_for('discutir', noticia_id=noticia_id))

    else: 
        comentarios = Comentario.obter_comentarios(noticia_id)
        if comentarios:
            return jsonify(comentarios), 200
        else:
            return jsonify({'message': 'Nenhum comentário encontrado para esta notícia.'}), 404

@app.route('/comentarios/deletar/<int:comentario_id>', methods=['DELETE'])
def deletar_comentario_route(comentario_id):
    if 'email' not in session:
        return jsonify({"erro": "Você precisa estar logado para deletar um comentário."}), 403

    resultado = Comentario.deletar_comentario(comentario_id)

    if resultado:
        return jsonify({"mensagem": "Comentário deletado com sucesso."}), 200
    else:
        return jsonify({"erro": "Erro ao deletar o comentário."}), 500


@app.route('/comentarios/editar/<int:comentario_id>', methods=['POST'])
def editar_comentario_route(comentario_id):
    if 'email' not in session:
        return jsonify({"erro": "Você precisa estar logado para editar um comentário."}), 403

    novo_conteudo = request.form.get('conteudo')
    if not novo_conteudo:
        return jsonify({"erro": "O conteúdo do comentário não pode estar vazio."}), 400

    resultado = Comentario.editar_comentario(comentario_id, novo_conteudo)

    if resultado:
        return jsonify({"mensagem": "Comentário editado com sucesso."}), 200
    else:
        return jsonify({"erro": "Erro ao editar o comentário."}), 500

@app.route('/criptomoeda', methods=['GET'])
def criptomoedas():
    dados = Criptomoedas.obter_criptomoedas()
    if isinstance(dados, dict) and "error" in dados:
        flash(dados["error"], "erro")
        return redirect(url_for('index')) 
    return render_template('criptomoeda.html', criptomoedas=dados)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'sucesso')
    return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True)