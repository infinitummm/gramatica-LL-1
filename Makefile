#!/usr/bin/make -f
# ==============================================================================
# Makefile Maestro - Compilador y Gramatica LL(1)
# Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
# Asignatura: Lenguajes de Programacion y Traduccion
# ==============================================================================

PYTHON ?= python3

.PHONY: all conjuntos test arbol interactivo clean help

all: conjuntos test

conjuntos:
	@$(PYTHON) main.py --conjuntos

test:
	@$(PYTHON) main.py --pruebas

arbol:
	@$(PYTHON) main.py --arbol

interactivo:
	@$(PYTHON) main.py --interactivo

clean:
	@echo "Limpiando caches de compilacion y archivos temporales..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "Limpieza completada."

help:
	@echo "Comandos disponibles en el Makefile:"
	@echo "  make             - Muestra los conjuntos LL(1), la tabla y ejecuta las pruebas"
	@echo "  make conjuntos   - Muestra los conjuntos PRIMEROS, SIGUIENTES, PRED y Tabla M[A, a]"
	@echo "  make test        - Ejecuta las baterias de prueba (exitosas y con errores)"
	@echo "  make arbol       - Muestra el arbol AST de los casos de exito y fracaso"
	@echo "  make interactivo - Inicia el interprete interactivo REPL"
	@echo "  make clean       - Limpia los directorios __pycache__ y temporales"
