import requests
from geopy.distance import geodesic
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter chave da API OpenCage do arquivo .env
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

def validar_cep(cep):
    """
    Valida um CEP usando a API ViaCEP.
    :param cep: CEP a ser validado (string).
    :return: Dados do endereço ou mensagem de erro.
    """
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        if "erro" in dados:
            return {"erro": "CEP inválido."}
        return dados
    else:
        return {"erro": "Erro ao acessar a API ViaCEP."}

def obter_coordenadas(endereco):
    """
    Obtém as coordenadas geográficas de um endereço usando a API OpenCage.
    :param endereco: Endereço completo (string).
    :return: Tupla com latitude e longitude ou mensagem de erro.
    """
    url = f"https://api.opencagedata.com/geocode/v1/json?q={endereco}&key={OPENCAGE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        if dados['results']:
            coordenadas = dados['results'][0]['geometry']
            return coordenadas['lat'], coordenadas['lng']
        else:
            return {"erro": "Coordenadas não encontradas para o endereço fornecido."}
    else:
        return {"erro": "Erro ao acessar a API OpenCage."}

def calcular_frete(cep_destino, cep_referencia="08750580", raio_km=5):
    """
    Calcula o custo do frete com base na distância entre dois CEPs.
    :param cep_destino: CEP de destino (string).
    :param cep_referencia: CEP de referência (string, padrão: 08750580).
    :param raio_km: Raio em km para a taxa base (int, padrão: 5).
    :return: Custo do frete ou mensagem de erro.
    """
    # Validar os CEPs e obter coordenadas
    dados_referencia = validar_cep(cep_referencia)
    dados_destino = validar_cep(cep_destino)

    if "erro" in dados_referencia:
        return {"erro": f"CEP de referência inválido: {dados_referencia['erro']}"}
    if "erro" in dados_destino:
        return {"erro": f"CEP de destino inválido: {dados_destino['erro']}"}

    try:
        endereco_referencia = f"{dados_referencia['logradouro']}, {dados_referencia['localidade']}, {dados_referencia['uf']}"
        endereco_destino = f"{dados_destino['logradouro']}, {dados_destino['localidade']}, {dados_destino['uf']}"

        coord_referencia = obter_coordenadas(endereco_referencia)
        coord_destino = obter_coordenadas(endereco_destino)

        if "erro" in coord_referencia:
            return coord_referencia
        if "erro" in coord_destino:
            return coord_destino

    except KeyError:
        return {"erro": "Dados insuficientes para obter coordenadas."}

    # Calcular a distância
    distancia_km = geodesic(coord_referencia, coord_destino).km

    # Calcular o custo do frete
    if distancia_km <= raio_km:
        custo = 5  # Taxa fixa de R$5 até 5 km
    else:
        custo = 5 + ((distancia_km - raio_km) * 1)  # R$1 por km adicional acima de 5 km

    return {"distancia_km": round(distancia_km, 2), "custo_frete": round(custo, 2)}

# Exemplo de uso
if __name__ == "__main__":
    cep_teste = "01001000"  # CEP de destino para teste
    resultado = calcular_frete(cep_teste)
    print(resultado)
