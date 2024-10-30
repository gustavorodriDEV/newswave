from flask import Flask, render_template, request, redirect, flash, url_for, session, make_response, jsonify
from config.db import conexao_db, fechar_conexao
from usuario import Usuario
from werkzeug.security import check_password_hash
from config.secret_key import Secret_key
from noticias import Noticias, salvar_noticias_db, buscar_noticias_db
from comentario_newswave import Comentario
from datetime import datetime

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

@app.route('/login', methods=['GET', 'POST'])
def login():  
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        
        usuario_classe = Usuario(None, None, None)
        usuario = usuario_classe.buscar_por_email(email)

        if usuario and check_password_hash(usuario[3], senha): 
            session['email'] = email 
            flash('Login realizado com sucesso!', 'sucesso')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'erro')
                
    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['email']
        senha = request.form['password']

        novo_usuario = Usuario(nome, email, senha)
        if novo_usuario.cadastrar_usuario():  
            flash('Cadastro realizado com sucesso!', 'sucesso')
            return redirect(url_for('login'))  
        else:
            flash('Erro ao cadastrar, tente novamente.', 'erro')
    
    return render_template('cadastro.html')

@app.route('/index')
def index():
    if 'email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'erro')
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

    response = make_response(render_template('index.html',
                                             email=session['email'], 
                                             articles=noticias_do_banco))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@app.route('/discutir/<int:noticia_id>')
def discutir(noticia_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    conn = conexao_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias WHERE id = %s", (noticia_id,))
    noticia = cursor.fetchone()

    comentarios = Comentario.obter_comentarios(noticia_id)

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
        usuario = usuario_classe.buscar_por_email(session['email'])
        
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)  
    flash('Logout realizado com sucesso.', 'sucesso')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
