from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from db import conexao_db, fechar_conexao

app = Flask(__name__) 

class Usuario:
    def __init__(self, nome, email, senha) :
        self.nome = nome
        self.email = email
        self.senha = senha

    def cadastrar_usuario(self):
        con = conexao_db()
        if con:
            try:
                cursor = con.cursor()
                senha_hash = generate_password_hash(self.senha)
                cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (self.nome, self.email, senha_hash))
                con.commit()
                return True  
            except Exception as e:
                print(f"Erro ao cadastrar: {e}")
                con.rollback()
                return False  
            finally:
                fechar_conexao(con)
        else:
            return False  
    def login(self):
            con = conexao_db()
            if con:
                try:
                    cursor = con.cursor()
                    cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (self.email,))
                    result = cursor.fetchone()

                    if result and result[0] == self.senha:  
                        flash('Login realizado com sucesso!', 'sucesso')
                        return redirect(url_for('index'))  # Redireciona para o index após o login bem-sucedido
                    else:
                        flash('Email ou senha incorretos.', 'erro')
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    fechar_conexao(con)
                    return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        usuario = request.args.get('usuario')
        if usuario:
            return f'Bem-vindo, {usuario}!'
        return redirect('/index')
