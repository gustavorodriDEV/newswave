import requests
from config.db import conexao_db, fechar_conexao
from config.api import Chave_api
from datetime import datetime
from comentario import Comentario


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
    try:
        # Estabelecendo conexão com o banco
        conn = conexao_db()
        cursor = conn.cursor()

        for noticia in noticias:
            # Obtendo os dados da notícia, com valores padrão se ausentes
            link = noticia.get('url', 'Link não disponível')[:500]  # Trunca o link
            titulo = noticia.get('title', 'Título não disponível')
            descricao = noticia.get('description', 'Descrição não disponível')
            imagemURL = noticia.get('urlToImage', 'Imagem não disponível')
            data_publicacao = noticia.get('publishedAt', None)
            autor = noticia.get('author', 'Autor não disponível')
            categoria = noticia.get('category', 'Categoria não informada')

            # Verificar duplicatas por link ou título
            cursor.execute("SELECT id FROM noticias WHERE link = %s OR titulo = %s", (link, titulo))
            resultado = cursor.fetchone()

            if resultado is None:
                # Formatar a data se disponível
                if data_publicacao:
                    data_publicacao = datetime.strptime(data_publicacao, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

                # Inserir a notícia no banco
                sql = """
                    INSERT INTO noticias (titulo, descricao, imagemURL, link, dataPublicacao, autor, categoria)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                valores = (titulo, descricao, imagemURL, link, data_publicacao, autor, categoria)
                cursor.execute(sql, valores)

        # Confirmar as alterações
        conn.commit()

    except Exception as e:
        # Tratar erros e desfazer mudanças no banco
        print(f"Erro ao salvar notícias: {e}")
        conn.rollback()

    finally:
        # Fechar recursos
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

def buscar_por_categoria(categoria):
    conn = conexao_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias WHERE categoria = %s", (categoria,))
    noticias_do_banco = cursor.fetchall()

    for noticia in noticias_do_banco:
        noticia_id = noticia.get('id')
        if noticia_id:
            noticia['comentarios_count'] = Comentario.contar_comentarios(noticia_id)
        else:
            noticia['comentarios_count'] = 0

    cursor.close()
    fechar_conexao(conn)
    return noticias_do_banco

