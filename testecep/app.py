from flask import Flask, request, render_template
from calculo_frete import calcular_frete, validar_cep, obter_coordenadas
from geopy.distance import geodesic

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('formulario.html')

@app.route('/calcular_frete', methods=['POST'])
def calcular():
    cep_referencia = request.form.get('cep_referencia')
    cep_destino = request.form.get('cep_destino')
    raio_km = float(request.form.get('raio_km'))
    valor_fixo = float(request.form.get('valor_fixo'))
    valor_adicional = float(request.form.get('valor_adicional'))

    def calcular_frete_customizado(cep_destino, cep_referencia, raio_km, valor_fixo, valor_adicional):
        dados_referencia = validar_cep(cep_referencia)
        dados_destino = validar_cep(cep_destino)

        if "erro" in dados_referencia:
            return {"erro": f"CEP de referência inválido: {dados_referencia['erro']}"}
        if "erro" in dados_destino:
            return {"erro": f"CEP de destino inválido: {dados_destino['erro']}"}

        endereco_referencia = f"{dados_referencia['logradouro']}, {dados_referencia['localidade']}, {dados_referencia['uf']}"
        endereco_destino = f"{dados_destino['logradouro']}, {dados_destino['localidade']}, {dados_destino['uf']}"
        coord_referencia = obter_coordenadas(endereco_referencia)
        coord_destino = obter_coordenadas(endereco_destino)

        if "erro" in coord_referencia:
            return coord_referencia
        if "erro" in coord_destino:
            return coord_destino

        distancia_km = geodesic(coord_referencia, coord_destino).km

        if distancia_km <= raio_km:
            custo = valor_fixo
        else:
            custo = valor_fixo + ((distancia_km - raio_km) * valor_adicional)

        return {"distancia_km": round(distancia_km, 2), "custo_frete": round(custo, 2)}

    resultado = calcular_frete_customizado(cep_destino, cep_referencia, raio_km, valor_fixo, valor_adicional)
    return f"<h1>Resultado: {resultado}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
