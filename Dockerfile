# Usamos uma imagem Python oficial e leve como base
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Impede que o Python grave arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Garante que a saída do Python seja exibida imediatamente nos logs
ENV PYTHONUNBUFFERED 1

# Copia o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte da aplicação (a pasta src) para o diretório de trabalho
COPY ./src .

# Comando que será executado quando o contêiner iniciar
CMD ["python", "main.py"]