# Projeto de Cálculo de Frete com Flask

Este projeto é uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele permite calcular o custo de frete com base na distância entre dois CEPs, considerando parâmetros configuráveis como raio padrão, valor fixo e valor adicional por quilômetro.

## Funcionalidades

- Validação de CEPs utilizando a API ViaCEP.
- Obtenção de coordenadas geográficas com a API OpenCage.
- Cálculo de frete com base na distância entre dois CEPs.
- Configuração de parâmetros de cálculo diretamente na interface web.

## Requisitos

- Python 3.10 ou superior
- Bibliotecas Python:
  - Flask
  - geopy
  - python-dotenv
  - requests

## Instalação

1. Clone este repositório:
   ```bash
   git clone <url-do-repositorio>
   ```

2. Navegue até o diretório do projeto:
   ```bash
   cd testecep
   ```

3. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate # Linux/Mac
   venv\Scripts\activate   # Windows
   ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API OpenCage:
   ```env
   OPENCAGE_API_KEY=your_api_key_here
   ```

## Uso

1. Inicie o servidor Flask:
   ```bash
   python app.py
   ```

2. Acesse a aplicação no navegador:
   ```
   http://127.0.0.1:5000/
   ```

3. Preencha os campos do formulário para calcular o frete.

## Estrutura do Projeto

```
├── app.py               # Arquivo principal da aplicação Flask
├── calculo_frete.py     # Lógica de validação de CEP e cálculo de frete
├── templates/           # Arquivos HTML
│   └── formulario.html  # Página do formulário
├── .env                 # Variáveis de ambiente (não versionado)
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação do projeto
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
