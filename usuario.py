from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from config.db import conexao_db, fechar_conexao

app = Flask(__name__)

class Usuario:
    def __init__(self, nome=None, email=None, senha=None):
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

    def buscar_por_email(self, email):
        con = conexao_db()
        if con:
            try:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                usuario = cursor.fetchone()
                return usuario
            except Exception as e:
                print(f"Erro ao buscar usuário: {e}")
                return None
            finally:
                fechar_conexao(con)

    def validar_login(self, senha_digitada):
        return check_password_hash(self.senha, senha_digitada)


