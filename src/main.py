import os
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def main():
    """
    Função principal que executa o loop do worker.
    """
    print("🚀 Worker service iniciado...")

    # Exemplo de como pegar variáveis de ambiente
    data_api_url = os.getenv("DATA_API_URL", "http://data-api-php:8000")
    scraper_service_url = os.getenv("SCRAPER_SERVICE_URL", "http://scraper-service-rust:8080")
    notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "http://notificador-service-go:8081")

    print(f"API de Dados: {data_api_url}")
    print(f"Serviço de Scraper: {scraper_service_url}")
    print(f"Serviço de Notificação: {notification_service_url}")

    while True:
        print("\nCiclo do worker iniciado...")
        # Lógica principal a ser implementada aqui
        # 1. Buscar produtos
        # 2. Para cada produto, chamar o scraper
        # 3. Atualizar preço
        # 4. Comparar e notificar se necessário
        print("Ciclo do worker finalizado. Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()