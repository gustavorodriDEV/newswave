from flask import Flask, render_template, request, redirect, flash, url_for, session, make_response
from config.db import conexao_db, fechar_conexao
from usuario import Usuario
from werkzeug.security import check_password_hash
from config.secret_key import Secret_key
from noticias import Noticias,salvar_noticias_db, buscar_noticias_db


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
        
        con = conexao_db()
        if con:
            try:
                cursor = con.cursor()
                cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (email,))
                result = cursor.fetchone()

                if result and check_password_hash(result[0], senha):
                    session['email'] = email 
                    flash('Login realizado com sucesso!', 'sucesso')
                    return redirect(url_for('index')) 
                else:
                    flash('Email ou senha incorretos.', 'erro')
            except Exception as e:
                print(f"Erro: {e}")
                flash('Erro ao realizar o login, tente novamente.', 'erro')
            finally:
                fechar_conexao(con)
                
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

    response = make_response(render_template('index.html', 
                                             email=session['email'], 
                                             articles=noticias_do_banco))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@app.route('/noticia_completa/<int:noticia_id>')
def noticia_completa(noticia_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    conn = conexao_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias WHERE id = %s", (noticia_id,))
    noticia = cursor.fetchone()
    cursor.close()
    fechar_conexao(conn)

    if noticia:
        response = make_response(render_template('noticia_completa.html', noticia=noticia))
        response.headers['Cache-Control'] = 'private, no-store, max-age=0, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    else:
        flash("Notícia não encontrada", "erro")
        return redirect(url_for('index'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)  
    flash('Logout realizado com sucesso.', 'sucesso')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
