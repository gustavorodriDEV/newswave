from config.db import conexao_db, fechar_conexao
from datetime import datetime

class Comentario:
    def __init__(self, conteudo, usuario_id, noticia_id):
        self.conteudo = conteudo
        self.usuario_id = usuario_id
        self.noticia_id = noticia_id

    def inserir_comentario(self):
        conn = conexao_db()
        cursor = conn.cursor()
        sql = """
            INSERT INTO comentarios (conteudo, data, usuario_id, noticia_id)
            VALUES (%s, %s, %s, %s)
        """
        valores = (self.conteudo, datetime.now(), self.usuario_id, self.noticia_id)
        
        try:
            cursor.execute(sql, valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir comentário: {e}")
            return False
        finally:
            cursor.close()
            fechar_conexao(conn)

    @staticmethod
    def obter_comentarios(noticia_id):
        conn = conexao_db()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT c.conteudo, c.data, u.nome
            FROM comentarios c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.noticia_id = %s;
        """
        try:
            cursor.execute(sql, (noticia_id,))
            comentarios = cursor.fetchall()
            return comentarios
        except Exception as e:
            print(f"Erro ao obter comentários: {e}")
            return []
        finally:
            cursor.close()
            fechar_conexao(conn)
 
    @staticmethod
    def contar_comentarios(noticia_id):
        try:
            conn = conexao_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM comentarios WHERE noticia_id = %s", (noticia_id,))
            total = cursor.fetchone()[0] 
            return total
        except Exception as e:
            print(f"Erro ao contar comentários: {e}")
            return 0
        finally:
            cursor.close()
            fechar_conexao(conn)
