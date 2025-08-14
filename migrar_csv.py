import pandas as pd
import re

def extrair_numero_whatsapp(telefone):
    """Extrai número limpo e gera link do WhatsApp"""
    if not telefone or pd.isna(telefone):
        return '', ''
    
    # Remove tudo exceto dígitos
    numero = re.sub(r'\D', '', str(telefone))
    
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

def migrar_dados():
    try:
        # Lê o CSV existente
        df = pd.read_csv('resultados.csv')
        
        # Cria as novas colunas
        df['palavra_chave'] = 'salão de beleza'  # valor padrão baseado no código
        df['cidade'] = 'São Paulo'
        df['bairro'] = 'N/A'
        df['data_coleta'] = '2025-01-14 00:00:00'  # data padrão
        
        # Reprocessa os números de WhatsApp para garantir consistência
        numeros_limpos = []
        whatsapp_links = []
        
        for _, row in df.iterrows():
            telefone_original = str(row['telefone']).replace('.0', '') if not pd.isna(row['telefone']) else ''
            numero, whatsapp = extrair_numero_whatsapp(telefone_original)
            if not numero and telefone_original:  # Se não conseguiu extrair, mantém o original
                numero = telefone_original
                whatsapp = f"https://wa.me/55{numero}" if len(numero) >= 10 else ''
            numeros_limpos.append(numero)
            whatsapp_links.append(whatsapp)
        
        df['telefone'] = numeros_limpos
        df['whatsapp'] = whatsapp_links
        
        # Filtra apenas contatos com WhatsApp válido
        df = df[df['whatsapp'] != '']
        
        # Reordena as colunas
        colunas_ordem = ['nome', 'endereco', 'telefone', 'whatsapp', 'palavra_chave', 'cidade', 'bairro', 'data_coleta']
        df = df[colunas_ordem]
        
        # Salva o novo CSV
        df.to_csv('resultados.csv', index=False)
        
        print(f"Migração concluída!")
        print(f"Total de contatos com WhatsApp: {len(df)}")
        
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrar_dados()