#
#
# Makefile for GloboNetworkAPI-WebUI
#
#


help:
	@echo
	@echo "Network API Web UI project"
	@echo
	@echo "Available target rules:"
	@echo
	@echo "  build      to build docker image locally"
	@echo "  start      to containers locally using docker-compose"
	@echo "  stop       to stop all project running containers"
	@echo "  restart    to restart main container"
	@echo "  logs       to follow logs of application container"
	@echo "  shell      to enter a shell on running container"
	@echo "  docs       to create documentation files"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  compile    to compile .py files (just to check for syntax errors)"
	@echo "  test       to execute all tests"
	@echo


build: Dockerfile
	@docker build . --no-cache


start: docker-compose.yml
	@docker-compose up --detach


stop: docker-compose.yml
	@docker-compose down --remove-orphans


restart:
	@docker restart netapi_webui_app


logs:
	@docker logs --tail 100 --follow netapi_webui_app


shell:
	@docker exec -it netapi_webui_app bash


clean:
	@echo "Cleaning..."
	@rm -rf build dist *.egg-info
	@rm -rf docs/_build
	@find . \( -name '*.pyc' -o -name '**/*.pyc' -o -name '*~' \) -delete


docs: clean
	@(cd docs && make html)


compile: clean
	@echo "Compiling source code..."
	@python -tt -m compileall .
	@pep8 --format=pylint --statistics networkapiclient setup.py
