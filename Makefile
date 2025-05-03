# Makefile para facilitar tarefas comuns

APP_NAME=discord-clockify-bot

build:
	docker build -t $(APP_NAME) .

run:
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/config:/app/config \
		$(APP_NAME)

dev:
	python run.py

requirements:
	pip freeze > requirements.txt

clean:
	rm -rf __pycache__ */__pycache__ *.pyc *.pyo

migrar:
	docker-compose exec discord-clockify-bot python -m web.commands.migrar_config_json
