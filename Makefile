# python local environment

.PHONY: venv
venv:
	python3.6 -m venv ./.venv

.PHONY: run
run:
	PY_ENV=local python main.py

# precommit environment

.PHONY: install_precommit
install_precommit:
	python3 -m pip install pre-commit; \
	python3 -m pip install flake8 pylint;
	pre-commit install; \
	pre-commit autoupdate;

# heroku environment

.PHONY: install_heroku
install_heroku:
	curl https://cli-assets.heroku.com/install.sh | sh

.PHONY: install_heroku_plugins
install_heroku:
	heroku plugins:install heroku-config

.PHONY: pull_config
pull_config:
	read -p "Please input your app name: " APP_NAME; \
	heroku config:pull -a $$APP_NAME;

.PHONY: push_config
push_config:
	read -p "Please input your app name: " APP_NAME; \
	heroku config:push -a $$APP_NAME;
