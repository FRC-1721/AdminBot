# Shortcut makefile list

help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


test: build ## Currently broken, requires build
	docker-compose run admin_bot test


configure-pipenv: ## sets up pipenv for you
	pipenv install -r admin_bot/requirements/requirements.txt
	pipenv install -r admin_interface/requirements/test_requirements.txt
	pipenv shell


build: ## Build containers locally
	# Generate tag
	echo TAG=$(shell git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9]/-/g') > .env

	# Build
	docker-compose build --build-arg GIT_COMMIT=$(shell git describe --abbrev=8 --always --tags --dirty) --build-arg DEBUG=True


docker-rm: stop  ## Delete containers, requires stop
	docker-compose rm -f


shell: ## Get container shell
	docker-compose run --entrypoint "/bin/bash" admin_bot


run: build ## Run command in container, requires build
	docker-compose up


stop: ## Stop containers
	docker-compose down
	docker-compose stop


dev: ## Build then run
	docker-compose -f docker-compose.yml build && docker-compose -f docker-compose.yml up
