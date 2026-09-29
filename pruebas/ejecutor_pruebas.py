"""
Ejecutor y validador integral de pruebas para el compilador LL(1).
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

import os
import sys

# Agregar la raiz del proyecto al path
DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIR_RAIZ not in sys.path:
    sys.path.insert(0, DIR_RAIZ)

from lexico import AnalizadorLexico
from sintactico import AnalizadorSintacticoLL1
from semantico import EvaluadorSemantico


def probar_casos_exitosos(ruta_archivo: str):
    print("=" * 80)
    print("PRUEBAS DE CASOS EXITOSOS")
    print(f"Archivo: {os.path.basename(ruta_archivo)}")
    print("=" * 80)

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        codigo = f.read()

    lexer = AnalizadorLexico(codigo)
    tokens = lexer.escanear_tokens()

    if lexer.errores:
        print("Fallo lexico en pruebas exitosas:")
        for err in lexer.errores:
            print("  *", err)
        return False

    parser = AnalizadorSintacticoLL1()
    pila_valida = parser.verificar_con_pila(tokens)
    print(f"Verificacion de pertenencia con pila LL(1): {'Valida' if pila_valida else 'Rechazada'}")

    ast = parser.analizar(tokens)
    if not ast:
        print("Fallo sintactico en pruebas exitosas:")
        for err in parser.errores:
            print("  *", err)
        return False

    print(f"AST construido correctamente: {len(ast.sentencias)} sentencias reconocidas.")

    evaluador = EvaluadorSemantico()
    resultado = evaluador.ejecutar_programa(ast)

    print("\nSalidas producidas por print():")
    for salida in resultado.salidas_impresion:
        print(f"  [SALIDA] {salida}")

    print("\nEstado final de la Tabla de Simbolos:")
    for simb in resultado.tabla_simbolos.listar_simbolos():
        print(f"  {simb.nombre:<20} = {str(simb.valor):<20} ({simb.tipo_dato})")

    if resultado.errores_semanticos:
        print("\nErrores semanticos detectados:")
        for err in resultado.errores_semanticos:
            print("  *", err)
        return False

    print("\nResultado global: Todas las pruebas exitosas pasaron correctamente.")
    return True


def probar_casos_errores(ruta_archivo: str):
    print("\n" + "=" * 80)
    print("PRUEBAS DE CAPTURA DE ERRORES (LEXICO, SINTACTICO Y SEMANTICO)")
    print(f"Archivo: {os.path.basename(ruta_archivo)}")
    print("=" * 80)

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    for i, linea in enumerate(lineas, start=1):
        print(f"\nCaso de prueba {i}: '{linea}'")
        lexer = AnalizadorLexico(linea)
        tokens = lexer.escanear_tokens()

        if lexer.errores:
            print(f"  [Error Lexico Detectado] {lexer.errores[0]}")
            continue

        parser = AnalizadorSintacticoLL1()
        ast = parser.analizar(tokens)

        if parser.errores:
            print(f"  [Error Sintactico Detectado] {parser.errores[0]}")
            continue

        if ast:
            evaluador = EvaluadorSemantico()
            res = evaluador.ejecutar_programa(ast)
            if res.errores_semanticos:
                print(f"  [Error Semantico Detectado] {res.errores_semanticos[0]}")
            else:
                print("  [Inesperado] La sentencia fue ejecutada sin errores.")


def main():
    dir_pruebas = os.path.dirname(os.path.abspath(__file__))
    archivo_exito = os.path.join(dir_pruebas, "casos_exito.txt")
    archivo_error = os.path.join(dir_pruebas, "casos_errores.txt")

    exito_ok = probar_casos_exitosos(archivo_exito)
    probar_casos_errores(archivo_error)


if __name__ == "__main__":
    main()
