import os
import time
import requests

# URLs dos outros serviços, obtidas das variáveis de ambiente
DATA_API_URL = os.getenv('DATA_API_URL')
SCRAPER_SERVICE_URL = os.getenv('SCRAPER_SERVICE_URL')
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL')

def buscar_produtos():
    """Busca a lista de produtos ativos na API de dados."""
    try:
        response = requests.get(f"{DATA_API_URL}/produtos")
        response.raise_for_status()
        print("Produtos buscados com sucesso.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar produtos: {e}")
        return []

def obter_preco_produto(url_produto):
    """Envia a URL para o serviço de scraping e obtém o preço."""
    try:
        response = requests.post(f"{SCRAPER_SERVICE_URL}/scrape", json={'url': url_produto})
        response.raise_for_status()
        return response.json().get('price')
    except requests.exceptions.RequestException as e:
        print(f"Erro no serviço de scraping: {e}")
        return None

def atualizar_preco_produto(produto_id, novo_preco):
    """Atualiza o preço de um produto na API de dados."""
    try:
        requests.put(f"{DATA_API_URL}/produtos/{produto_id}", json={'preco_atual': novo_preco})
        print(f"Preço do produto {produto_id} atualizado para {novo_preco}.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar preço: {e}")

def enviar_notificacao(contato_id, mensagem):
    """Aciona o serviço de notificação para enviar um alerta."""
    try:
        # Primeiro, busca os dados do contato para obter o chat_id
        contato_response = requests.get(f"{DATA_API_URL}/contatos/{contato_id}")
        contato_response.raise_for_status()
        chat_id = contato_response.json().get('telegram_chat_id')

        if not chat_id:
            print(f"Erro: telegram_chat_id não encontrado para o contato_id {contato_id}")
            return

        # Envia a notificação
        notification_payload = {'chat_id': chat_id, 'mensagem': mensagem}
        requests.post(f"{NOTIFICATION_SERVICE_URL}/notificacao", json=notification_payload)
        print(f"Notificação enviada para o chat_id: {chat_id}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar contato ou enviar notificação: {e}")


def main():
    """Função principal que executa o ciclo do worker."""
    print("🚀 Worker service iniciado...")
    print(f"API de Dados: {DATA_API_URL}")
    print(f"Serviço de Scraper: {SCRAPER_SERVICE_URL}")
    print(f"Serviço de Notificação: {NOTIFICATION_SERVICE_URL}")
    print("\n" + "="*50)

    while True:
        print("Ciclo do worker iniciado...")
        produtos = buscar_produtos()

        if not produtos:
            print("Nenhum produto encontrado para verificação.")
        else:
            for produto in produtos:
                produto_id = produto.get('id')
                produto_nome = produto.get('nome')
                produto_url = produto.get('url')
                preco_alvo = float(produto.get('preco_alvo', 0))

                print(f"\n--- Processando produto: {produto_nome} (ID: {produto_id}) ---")

                if not produto_url:
                    print(f"URL não encontrada para o produto {produto_nome}. Pulando.")
                    continue

                preco_atual_str = obter_preco_produto(produto_url)

                if preco_atual_str is not None:
                    try:
                        preco_atual = float(preco_atual_str)
                        atualizar_preco_produto(produto_id, preco_atual)

                        if preco_atual <= preco_alvo:
                            print(f"ALERTA! Preço alvo atingido para {produto_nome}!")
                            mensagem = f"🎉 Alerta de Preço! 🎉\n\nO produto '{produto_nome}' atingiu o preço alvo de R$ {preco_alvo:.2f}!\n\nPreço atual: R$ {preco_atual:.2f}\n\nCompre agora: {produto_url}"
                            enviar_notificacao(produto.get('contato_id'), mensagem)
                        else:
                            print(f"Preço atual (R$ {preco_atual:.2f}) ainda acima do alvo (R$ {preco_alvo:.2f}).")

                    except (ValueError, TypeError):
                        print(f"Erro ao converter o preço '{preco_atual_str}' para float.")
                else:
                    print(f"Falha ao obter o preço para o produto {produto_nome}.")

        print("="*50 + "\nCiclo do worker finalizado. Aguardando 60 segundos...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()