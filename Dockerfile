# Dockerfile para execução do bot Discord-Clockify

FROM python:3.11-slim

# Diretório de trabalho no container
WORKDIR /app

# Copiar dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

# Variável de ambiente padrão (pode ser sobreposta no docker run)
ENV PYTHONUNBUFFERED=1

# Comando de execução padrão
CMD ["python", "run.py"]
