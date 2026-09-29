"""
Punto de Entrada Principal del Compilador LL(1).
Asignatura: Lenguajes de Programacion y Traduccion
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

import sys
import os

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIR_ACTUAL not in sys.path:
    sys.path.insert(0, DIR_ACTUAL)

from lexico import AnalizadorLexico
from sintactico import GramaticaLL1, CalculadorConjuntosLL1, TablaAnalisisLL1, AnalizadorSintacticoLL1
from semantico import EvaluadorSemantico, TablaSimbolos


def mostrar_conjuntos_y_tabla():
    gramatica = GramaticaLL1()
    calculador = CalculadorConjuntosLL1(gramatica)
    tabla = TablaAnalisisLL1(gramatica, calculador)

    print(tabla.generar_reporte_conjuntos())
    print("\n" + tabla.generar_tabla_visual())


def ejecutar_archivo(ruta_archivo: str, mostrar_trazas: bool = False):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        return

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        codigo = f.read()

    print("=" * 80)
    print(f"COMPILANDO Y EJECUTANDO ARCHIVO: {os.path.basename(ruta_archivo)}")
    print("=" * 80)

    # 1. Analisis Lexico
    lexer = AnalizadorLexico(codigo)
    tokens = lexer.escanear_tokens()

    if lexer.errores:
        print("Errores lexicos detectados:")
        for err in lexer.errores:
            print("  *", err)
        return

    # 2. Analisis Sintactico LL(1)
    parser = AnalizadorSintacticoLL1()
    valido_pila = parser.verificar_con_pila(tokens)
    print(f"Fase Sintactica (Pila y Tabla M[A, a]): {'Aceptada' if valido_pila else 'Rechazada'}")

    if mostrar_trazas:
        print("\nPrimeros 15 pasos de derivacion en pila:")
        for i, (pila, entrada, accion) in enumerate(parser.trazas_pila[:15], start=1):
            print(f"  Paso {i:2d} | Pila: {pila:<30} | Entrada: {entrada:<20} | Accion: {accion}")

    ast = parser.analizar(tokens)
    if not ast or parser.errores:
        print("Errores sintacticos detectados:")
        for err in parser.errores:
            print("  *", err)
        return

    print(f"AST generado con exito ({len(ast.sentencias)} sentencias).")

    # 3. Analisis Semantico y Ejecucion
    evaluador = EvaluadorSemantico()
    resultado = evaluador.ejecutar_programa(ast)

    if resultado.salidas_impresion:
        print("\nSalidas en consola:")
        for s in resultado.salidas_impresion:
            print(f"  [SALIDA] {s}")

    print("\nTabla de Simbolos final:")
    for simb in resultado.tabla_simbolos.listar_simbolos():
        print(f"  {simb.nombre:<20} = {str(simb.valor):<20} ({simb.tipo_dato})")

    if resultado.errores_semanticos:
        print("\nErrores semanticos detectados:")
        for err in resultado.errores_semanticos:
            print("  *", err)


def modo_interactivo():
    print("=" * 80)
    print("CONSOLA INTERACTIVA - COMPILADOR LL(1)")
    print("Soporte: +, -, *, /, %, abs, sin, cos, tan, asignacion y print()")
    print("Escriba 'salir' o presione Ctrl+C para terminar.")
    print("=" * 80)

    tabla_simbolos = TablaSimbolos()
    parser = AnalizadorSintacticoLL1()
    evaluador = EvaluadorSemantico(tabla_simbolos)

    while True:
        try:
            linea = input("LL(1)> ").strip()
            if not linea:
                continue
            if linea.lower() in ('salir', 'exit', 'quit'):
                break

            # Asegurar punto y coma al final si falta para comodidad del usuario
            if not linea.endswith(';'):
                linea += ';'

            lexer = AnalizadorLexico(linea)
            tokens = lexer.escanear_tokens()

            if lexer.errores:
                for err in lexer.errores:
                    print("  [Error Lexico]", err)
                continue

            ast = parser.analizar(tokens)
            if not ast or parser.errores:
                for err in parser.errores:
                    print("  [Error Sintactico]", err)
                continue

            res = evaluador.ejecutar_programa(ast)
            for salida in res.salidas_impresion:
                print("  =>", salida)
            for paso in res.pasos_ejecucion:
                if paso.tipo_accion != "Impresion":
                    print(f"  [{paso.tipo_accion}] {paso.descripcion}")

            if res.errores_semanticos:
                for err in res.errores_semanticos:
                    print("  [Error Semantico]", err)

        except (KeyboardInterrupt, EOFError):
            print("\nFinalizando sesion interactiva.")
            break
        except Exception as ex:
            print("  [Error Inesperado]:", ex)


def mostrar_arboles_pruebas():
    """
    Visualiza la estructura jerarquica del Arbol de Sintaxis Abstracta (AST)
    para los casos de exito y analiza que ocurre con los casos de fracaso.
    """
    from sintactico import arbol_ast_a_texto

    ruta_exito = os.path.join(DIR_ACTUAL, "pruebas", "casos_exito.txt")
    ruta_error = os.path.join(DIR_ACTUAL, "pruebas", "casos_errores.txt")

    print("=" * 80)
    print("VISUALIZACION DEL ARBOL DE SINTAXIS ABSTRACTA (AST) - CASOS DE EXITO")
    print(f"Archivo analizado: {os.path.basename(ruta_exito)}")
    print("=" * 80)

    if os.path.exists(ruta_exito):
        with open(ruta_exito, "r", encoding="utf-8") as f:
            codigo_exito = f.read()

        lexer = AnalizadorLexico(codigo_exito)
        tokens = lexer.escanear_tokens()
        parser = AnalizadorSintacticoLL1()
        ast = parser.analizar(tokens)

        if ast:
            print(f"\nPrograma compilado exitosamente: {len(ast.sentencias)} sentencias reconocidas.\n")
            for i, sentencia in enumerate(ast.sentencias, start=1):
                print(f"--- [Sentencia {i:02d}] ---")
                print(arbol_ast_a_texto(sentencia))
                print()
        else:
            print("No se pudo generar el AST de casos exitosos.")
    else:
        print(f"Archivo no encontrado: {ruta_exito}")

    print("=" * 80)
    print("ANALISIS DE ARBOLES (AST) EN CASOS DE ERROR Y FRACASO")
    print(f"Archivo analizado: {os.path.basename(ruta_error)}")
    print("=" * 80)

    if os.path.exists(ruta_error):
        with open(ruta_error, "r", encoding="utf-8") as f:
            lineas_error = [l.strip() for l in f if l.strip() and not l.startswith("#")]

        for idx, linea in enumerate(lineas_error, start=1):
            print(f"\n>>> [Caso de Fracaso {idx:02d}] Entrada: {linea}")

            # 1. Fase Lexica
            lex = AnalizadorLexico(linea)
            toks = lex.escanear_tokens()
            if lex.errores:
                print("  * Fase Lexica    : RECHAZADA")
                print(f"  * Diagnostico    : {lex.errores[0]}")
                print("  * Estado del AST : NO SE PUDO GENERAR (Infraccion del alfabeto del lenguaje)")
                continue

            # 2. Fase Sintactica
            prs = AnalizadorSintacticoLL1()
            ast_err = prs.analizar(toks)
            if prs.errores or not ast_err:
                err_msg = prs.errores[0] if prs.errores else "Infraccion de reglas gramaticales"
                print("  * Fase Lexica    : ACEPTADA")
                print("  * Fase Sintactica: RECHAZADA")
                print(f"  * Diagnostico    : {err_msg}")
                print("  * Estado del AST : NO SE PUDO GENERAR (Cadena sintacticamente invalida)")
                continue

            # 3. Fase Semantica (Aqui la sintaxis es valida y SI hay AST, pero falla la semantica)
            print("  * Fase Lexica    : ACEPTADA")
            print("  * Fase Sintactica: ACEPTADA (Estructura gramaticalmente valida)")
            print("  * Arbol AST Generado por el Parser:")
            for sent in ast_err.sentencias:
                for linea_arbol in arbol_ast_a_texto(sent).splitlines():
                    print(f"      {linea_arbol}")

            evaluador = EvaluadorSemantico()
            res = evaluador.ejecutar_programa(ast_err)
            if res.errores_semanticos:
                print("  * Fase Semantica : RECHAZADA (Error en tiempo de evaluacion/tipos)")
                print(f"  * Diagnostico    : {res.errores_semanticos[0]}")
            else:
                print("  * Fase Semantica : ACEPTADA (Sentencia auxiliar valida)")
    else:
        print(f"Archivo no encontrado: {ruta_error}")
    print("\n" + "=" * 80)


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('--conjuntos', '-c', 'conjuntos'):
            mostrar_conjuntos_y_tabla()
        elif arg in ('--pruebas', '-p', 'pruebas'):
            from pruebas.ejecutor_pruebas import main as correr_pruebas
            correr_pruebas()
        elif arg in ('--arbol', '-a', 'arbol'):
            mostrar_arboles_pruebas()
        elif arg in ('--interactivo', '-i'):
            modo_interactivo()
        elif arg in ('--archivo', '-f') and len(sys.argv) > 2:
            ejecutar_archivo(sys.argv[2], mostrar_trazas=('--trazas' in sys.argv))
        elif os.path.exists(sys.argv[1]):
            ejecutar_archivo(sys.argv[1], mostrar_trazas=('--trazas' in sys.argv))
        else:
            print("Uso:")
            print("  python3 main.py --conjuntos   : Muestra PRIMEROS, SIGUIENTES, PRED y Tabla LL(1)")
            print("  python3 main.py --pruebas     : Ejecuta la bateria completa de pruebas")
            print("  python3 main.py --arbol       : Muestra los Arboles AST de exito y fracaso")
            print("  python3 main.py --interactivo : Inicia la consola REPL interactiva")
            print("  python3 main.py <archivo.txt> : Compila y ejecuta un archivo")
    else:
        # Por defecto muestra los conjuntos y corre las pruebas
        mostrar_conjuntos_y_tabla()
        print("\n")
        from pruebas.ejecutor_pruebas import main as correr_pruebas
        correr_pruebas()


if __name__ == "__main__":
    main()
