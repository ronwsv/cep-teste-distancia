
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import re


# Configurações
PALAVRA_CHAVE = "salão de beleza"  # Altere para a palavra-chave desejada
CIDADE = "São Paulo"         # Altere para a cidade desejada
BAIRRO = "Cidade Tiradentes"                  # Altere para o bairro desejado ou deixe vazio
NUM_PAGINAS = 10             # Quantidade de "rolagens" para buscar mais resultados

def extrair_numero_whatsapp(telefone):
    """Extrai número limpo e gera link do WhatsApp"""
    if not telefone:
        return '', ''
    
    # Remove tudo exceto dígitos
    numero = re.sub(r'\D', '', telefone)
    
    # Validação mais rigorosa para números brasileiros
    if len(numero) == 11 and numero.startswith('11'):  # Celular SP
        return numero, f"https://wa.me/55{numero}"
    elif len(numero) == 10 and numero.startswith('11'):  # Fixo SP
        return numero, f"https://wa.me/55{numero}"
    elif len(numero) == 13 and numero.startswith('5511'):  # Com código país
        return numero[2:], f"https://wa.me/{numero}"
    elif 10 <= len(numero) <= 11:  # Outros estados
        return numero, f"https://wa.me/55{numero}"
    
    return '', ''

def main():

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    # User-Agent customizado para simular navegador real
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    
    # Monta busca mais específica incluindo bairro na cidade quando informado
    if BAIRRO.strip():
        busca = f"{PALAVRA_CHAVE} {BAIRRO}, {CIDADE}"
    else:
        busca = f"{PALAVRA_CHAVE} {CIDADE}"
    
    print(f"Buscando: {busca}")
    url = f"https://www.google.com/maps/search/{'+'.join(busca.split())}"
    driver.get(url)
    time.sleep(random.uniform(6, 10))  # Delay inicial maior


    # Carrega contatos já salvos para evitar repetições
    try:
        df_existente = pd.read_csv('resultados.csv')
        contatos_existentes = set(df_existente['telefone'].dropna().astype(str))
        nomes_enderecos_existentes = set((str(n).strip().lower(), str(e).strip().lower()) for n, e in zip(df_existente['nome'], df_existente['endereco']))
    except Exception:
        contatos_existentes = set()
        nomes_enderecos_existentes = set()

    resultados = []
    visitados = set()


    for _ in range(NUM_PAGINAS):
        estabelecimentos = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
        for est in estabelecimentos:
            link = est.get_attribute('href')
            if link in visitados:
                continue
            visitados.add(link)
            try:
                # Simula movimento humano antes do clique
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", est)
                time.sleep(random.uniform(1.5, 3.5))
                driver.execute_script("arguments[0].click();", est)
                time.sleep(random.uniform(3.5, 7.5))
                nome = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text.strip()
                # Busca por telefone em múltiplos seletores
                telefone = ''
                try:
                    # Primeiro tenta o seletor principal
                    telefone_elem = driver.find_element(By.CSS_SELECTOR, 'button[data-tooltip*="telefone"]')
                    telefone = telefone_elem.get_attribute('aria-label')
                except:
                    try:
                        # Tenta outros seletores possíveis
                        telefone_elem = driver.find_element(By.CSS_SELECTOR, 'button[data-value*="phone"]')
                        telefone = telefone_elem.get_attribute('aria-label')
                    except:
                        try:
                            # Busca por texto que contenha números de telefone
                            telefones_text = driver.find_elements(By.XPATH, "//span[contains(text(), '(11)') or contains(text(), '11 ')]")
                            if telefones_text:
                                telefone = telefones_text[0].text
                        except:
                            telefone = ''
                
                # Limpa o texto do telefone
                if telefone:
                    telefone = re.sub(r'[^\d()+-]', '', telefone)
                try:
                    endereco = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').text.strip()
                except:
                    endereco = ''
                numero, whatsapp = extrair_numero_whatsapp(telefone)
                
                # Filtra pelo bairro se informado (filtro mais rigoroso)
                if BAIRRO.strip():
                    bairro_normalizado = BAIRRO.strip().lower().replace('ã','a').replace('á','a').replace('à','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
                    endereco_normalizado = endereco.lower().replace('ã','a').replace('á','a').replace('à','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
                    nome_normalizado = nome.lower().replace('ã','a').replace('á','a').replace('à','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
                    
                    # Verifica se o bairro está no endereço ou nome do estabelecimento
                    if bairro_normalizado not in endereco_normalizado and bairro_normalizado not in nome_normalizado:
                        print(f"Filtrado: {nome} - {endereco} (bairro {BAIRRO} não encontrado)")
                        continue
                    else:
                        print(f"Encontrado no bairro {BAIRRO}: {nome} - {endereco}")
                # Só adiciona se tiver WhatsApp válido
                if not numero or not whatsapp:
                    print(f"Sem WhatsApp: {nome}")
                    continue
                
                # Verifica se já existe pelo telefone ou pelo par nome/endereço
                if (numero and numero in contatos_existentes) or ((nome.lower(), endereco.lower()) in nomes_enderecos_existentes):
                    print(f"Duplicado: {nome} - {numero}")
                    continue
                
                print(f"✓ Adicionado: {nome} - {numero}")
                resultados.append({
                    'nome': nome,
                    'endereco': endereco,
                    'telefone': numero,
                    'whatsapp': whatsapp,
                    'palavra_chave': PALAVRA_CHAVE,
                    'cidade': CIDADE,
                    'bairro': BAIRRO if BAIRRO.strip() else 'N/A',
                    'data_coleta': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                continue
        # Simula rolagem humana e espera aleatória
        for _ in range(random.randint(2, 4)):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(1.5, 3.5))
        time.sleep(random.uniform(5, 10))

    # Salva resultados novos junto com os antigos, sem duplicar
    if resultados:
        try:
            df_existente = pd.read_csv('resultados.csv')
            df_novos = pd.DataFrame(resultados)
            df_final = pd.concat([df_existente, df_novos], ignore_index=True).drop_duplicates()
            df_final.to_csv('resultados.csv', index=False)
        except Exception:
            pd.DataFrame(resultados).drop_duplicates().to_csv('resultados.csv', index=False)
    driver.quit()
    
    # Relatório final
    total_com_whatsapp = len([r for r in resultados if r.get('whatsapp')])
    print(f'\n=== RELATÓRIO FINAL ===')
    print(f'Busca: {PALAVRA_CHAVE} em {CIDADE}' + (f' - {BAIRRO}' if BAIRRO.strip() else ''))
    print(f'Novos contatos encontrados: {len(resultados)}')
    print(f'Contatos com WhatsApp: {total_com_whatsapp}')
    print(f'Arquivo salvo: resultados.csv')
    print(f'Total no arquivo: {len(pd.read_csv("resultados.csv")) if resultados else "N/A"}')

if __name__ == "__main__":
    main()
