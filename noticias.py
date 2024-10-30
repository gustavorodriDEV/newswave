from flask import Flask, render_template
import requests
from config.db import conexao_db, fechar_conexao
from config.api import Chave_api
from datetime import datetime

app = Flask(__name__)

chave = Chave_api()
api_key = chave.news_api()

ENABLE_API_CONSUMPTION = False

if ENABLE_API_CONSUMPTION:
    response = requests.get("https://newsapi.org/v2/top-headlines")

class Noticias:
    def __init__(self):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def buscar_noticias(self, pais='us', categoria='Sports'):
        params = {
            'country': pais,
            'category': categoria,
            'apiKey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            articles = response.json()['articles']
        
            for article in articles:
                article['category'] = categoria 
            return articles
        else:
            print(f"Erro: {response.status_code}")
            return None

def salvar_noticias_db(noticias):
    conn = conexao_db()
    cursor = conn.cursor()

    for noticia in noticias:

        link = noticia.get('url', 'Link não disponível')

        if len(link) > 500:
           link = link[:500] 

        titulo = noticia.get('title', 'Título não disponível')
        descricao = noticia.get('description', 'Descrição não disponível')
        imagemURL = noticia.get('urlToImage', 'Imagem não disponível')
        data_publicacao = noticia.get('publishedAt', None)
        autor = noticia.get('author', 'Autor não disponível')
        categoria = noticia.get('category', 'Categoria não informada')

        cursor.execute("SELECT id FROM noticias WHERE link = %s", (link,))
        resultado = cursor.fetchone()

        if resultado is None:
            if data_publicacao:
                data_publicacao = datetime.strptime(data_publicacao, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

            sql = """
            INSERT INTO noticias (titulo, descricao, imagemURL, link, dataPublicacao, autor, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            valores = (titulo, descricao, imagemURL, link, data_publicacao, autor, categoria)
            cursor.execute(sql, valores)

    conn.commit()
    cursor.close()
    fechar_conexao(conn)

def buscar_noticias_db():
    conn = conexao_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id,titulo, descricao, imagemURL, link, dataPublicacao, autor, categoria FROM noticias")
    noticias = cursor.fetchall()
    cursor.close()
    fechar_conexao(conn)
    return noticias


def buscar_por_id(self, noticia_id):
        conn = conexao_db()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM noticias WHERE id = %s"
        cursor.execute(sql, (noticia_id,))
        noticia = cursor.fetchone()
        cursor.close()
        fechar_conexao(conn)
        return noticia
