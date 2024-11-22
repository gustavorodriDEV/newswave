import requests

class Criptomoedas:
    @staticmethod
    def obter_criptomoedas():
        url = "https://api.coingecko.com/api/v3/coins/markets"
        parametros = {
            "vs_currency": "brl", 
            "order": "market_cap_desc", 
            "per_page": 29, 
            "page": 1, 
            "sparkline": False  
        }

        try:
            resposta = requests.get(url, params=parametros)
            resposta.raise_for_status()
            return resposta.json()  # Retorna os dados como lista de dicionários
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao acessar a API: {str(e)}"}
        except Exception as e:
            return {"error": f"Erro inesperado: {str(e)}"}
