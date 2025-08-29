import os
import time
import requests
import json
from decimal import Decimal, InvalidOperation


def get_active_products(api_url):
    """Busca a lista de produtos ativos na API de Dados."""
    try:
        response = requests.get(f"{api_url}/produtos")
        response.raise_for_status()  # Lança um erro para respostas 4xx/5xx
        print("Produtos buscados com sucesso.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar produtos: {e}")
        return []

def get_current_price(scraper_url, product_url):
    """Invoca o serviço de scraper para obter o preço atual de um produto."""
    try:
        payload = {"url": product_url}
        response = requests.post(f"{scraper_url}/scrape", json=payload)
        response.raise_for_status()
        price_str = response.json().get("price")
        
        # Limpa e converte o preço para Decimal para precisão
        cleaned_price_str = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        price = Decimal(cleaned_price_str)

        print(f"Preço obtido para {product_url}: R$ {price}")
        return price
    except (requests.exceptions.RequestException, InvalidOperation, TypeError, KeyError) as e:
        print(f"Falha ao obter ou processar o preço para {product_url}: {e}")
        return None

def update_product_price(api_url, product_id, new_price):
    """Atualiza o preço atual do produto na API de Dados."""
    try:
        # A API espera um float ou string, então convertemos Decimal para string
        payload = {"preco_atual": str(new_price)}
        response = requests.put(f"{api_url}/produtos/{product_id}", json=payload)
        response.raise_for_status()
        print(f"Preço do produto {product_id} atualizado para R$ {new_price}.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar o preço do produto {product_id}: {e}")

def send_notification(notifier_url, product, contact):
    """Envia uma notificação se o preço atingir o alvo."""
    try:
        payload = {
            "productName": product.get("nome_produto"),
            "productURL": product.get("url_produto"),
            "price": str(product.get("preco_atual")),
            "contact": contact # O número de telefone do contato associado
        }
        response = requests.post(f"{notifier_url}/notify", json=json.dumps(payload))
        response.raise_for_status()
        print(f"Notificação enviada para o produto {product.get('nome_produto')}!")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar notificação para {product.get('nome_produto')}: {e}")

def main():
    """
    Função principal que executa o loop do worker.
    """
    print("🚀 Worker service iniciado...")

    data_api_url = os.getenv("DATA_API_URL")
    scraper_service_url = os.getenv("SCRAPER_SERVICE_URL")
    notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL")

    if not all([data_api_url, scraper_service_url, notification_service_url]):
        print("Erro: Variáveis de ambiente (DATA_API_URL, SCRAPER_SERVICE_URL, NOTIFICATION_SERVICE_URL) não definidas.")
        return

    print(f"API de Dados: {data_api_url}")
    print(f"Serviço de Scraper: {scraper_service_url}")
    print(f"Serviço de Notificação: {notification_service_url}")
    
    while True:
        print("\n" + "="*50)
        print("Ciclo do worker iniciado...")
        
        products = get_active_products(data_api_url)

        if not products:
            print("Nenhum produto encontrado para verificação.")
        
        for product in products:
            product_id = product.get("id")
            product_url = product.get("url_produto")
            print(f"\n--- Processando produto: {product.get('nome_produto')} (ID: {product_id}) ---")

            current_price = get_current_price(scraper_service_url, product_url)

            if current_price is not None:
                update_product_price(data_api_url, product_id, current_price)
                
                try:
                    # Precisamos garantir que o preco_alvo também seja um Decimal para comparação
                    target_price = Decimal(product.get("preco_alvo"))
                    
                    if current_price <= target_price:
                        print(f"PREÇO ATINGIDO! Preço atual: R${current_price}, Preço-alvo: R${target_price}")
                        # A API de dados precisa retornar o contato junto com o produto
                        contact_number = product.get("contato", {}).get("telefone")
                        if contact_number:
                             send_notification(notification_service_url, product, contact_number)
                        else:
                            print("Contato não encontrado para este produto. Notificação não enviada.")
                    else:
                        print(f"Preço atual (R${current_price}) ainda acima do alvo (R${target_price}).")

                except (InvalidOperation, TypeError) as e:
                    print(f"Preço-alvo inválido para o produto {product_id}: {product.get('preco_alvo')}. Erro: {e}")

        print("="*50)
        print("Ciclo do worker finalizado. Aguardando 60 segundos...")
        time.sleep(60)

if __name__ == "__main__":
    main()