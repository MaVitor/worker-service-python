# Worker Service (Python)

## Visão Geral

Este microsserviço atua como o **maestro** da Plataforma de Alerta de Preços da Amazon. Escrito em Python, ele contém a lógica de negócio principal, orquestrando os outros serviços para automatizar o processo de verificação de preços e envio de notificações.

Sua principal responsabilidade é rodar em um ciclo contínuo para garantir que os preços dos produtos cadastrados estejam sempre atualizados e que os alertas sejam enviados assim que um preço-alvo for atingido.

## Tecnologias Utilizadas

-   **Python 3.12:** Linguagem principal, escolhida por sua simplicidade e robustez para scripts de automação e tarefas de orquestração.
-   **Requests:** Biblioteca para realizar chamadas HTTP aos outros microsserviços da plataforma.
-   **Docker:** Para containerizar a aplicação, garantindo um ambiente de execução consistente e isolado.

## Funcionalidades

-   Busca a lista de produtos ativos na `data-api-php`.
-   Para cada produto, invoca o `scraper-service-rust` para obter o preço atual.
-   Atualiza o `preco_atual` do produto na `data-api-php`.
-   Compara o `preco_atual` com o `preco_alvo`.
-   Caso o preço seja igual ou menor que o alvo, aciona o `notificador-service-go` para enviar o alerta.

## Variáveis de Ambiente

Para se comunicar com os outros serviços, este worker depende das seguintes variáveis de ambiente, que são injetadas pelo `docker-compose.yml`:

| Variável                 | Descrição                                         | Exemplo                              |
| ------------------------ | ------------------------------------------------- | ------------------------------------ |
| `DATA_API_URL`           | URL base do serviço de dados (PHP).               | `http://api:8000`                    |
| `SCRAPER_SERVICE_URL`    | URL base do serviço de scraping (Rust).           | `http://scraper:8082`                |
| `NOTIFICATION_SERVICE_URL` | URL base do serviço de notificação (Go). | `http://notifier:8080`               |

---