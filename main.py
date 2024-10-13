from flask import Flask, render_template, request, redirect, flash, url_for, session
from db import conexao_db, fechar_conexao
from usuario import Usuario
from werkzeug.security import check_password_hash
from secret_key import Secret_key

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('teste.html')

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
    if 'email' in session:  
        return render_template('index.html', email=session['email'])
    else:
        flash('Você precisa fazer login para acessar esta página.', 'erro')
        return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)  
    flash('Logout realizado com sucesso.', 'sucesso')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
