"""
Estructuras de datos para el Arbol de Sintaxis Abstracta (AST).
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import List, Union, Optional


class NodoAST:
    pass


class NodoPrograma(NodoAST):
    def __init__(self, sentencias: List['NodoSentencia']):
        self.sentencias = sentencias

    def __repr__(self) -> str:
        return f"Programa({len(self.sentencias)} sentencias)"


class NodoSentencia(NodoAST):
    pass


class NodoAsignacion(NodoSentencia):
    def __init__(self, variable: str, expresion: 'NodoExpr', linea: int = 1, columna: int = 1):
        self.variable = variable
        self.expresion = expresion
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"Asignacion({self.variable} = {self.expresion})"


class NodoPrint(NodoSentencia):
    def __init__(self, expresion: 'NodoExpr', linea: int = 1, columna: int = 1):
        self.expresion = expresion
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"Print({self.expresion})"


class NodoEvaluacionExpresion(NodoSentencia):
    def __init__(self, expresion: 'NodoExpr', linea: int = 1, columna: int = 1):
        self.expresion = expresion
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"Eval({self.expresion})"


class NodoExpr(NodoAST):
    def __init__(self, linea: int = 1, columna: int = 1):
        self.linea = linea
        self.columna = columna


class NodoBinario(NodoExpr):
    def __init__(self, operador: str, izq: NodoExpr, der: NodoExpr, linea: int = 1, columna: int = 1):
        super().__init__(linea, columna)
        self.operador = operador
        self.izq = izq
        self.der = der

    def __repr__(self) -> str:
        return f"Binario({self.izq} {self.operador} {self.der})"


class NodoUnario(NodoExpr):
    def __init__(self, operador: str, operando: NodoExpr, linea: int = 1, columna: int = 1):
        super().__init__(linea, columna)
        self.operador = operador
        self.operando = operando

    def __repr__(self) -> str:
        return f"Unario({self.operador}{self.operando})"


class NodoFuncion(NodoExpr):
    def __init__(self, nombre: str, argumento: NodoExpr, linea: int = 1, columna: int = 1):
        super().__init__(linea, columna)
        self.nombre = nombre
        self.argumento = argumento

    def __repr__(self) -> str:
        return f"Funcion({self.nombre}({self.argumento}))"


class NodoNumero(NodoExpr):
    def __init__(self, valor: Union[int, float], linea: int = 1, columna: int = 1):
        super().__init__(linea, columna)
        self.valor = valor

    def __repr__(self) -> str:
        return f"Num({self.valor})"


class NodoIdentificador(NodoExpr):
    def __init__(self, nombre: str, linea: int = 1, columna: int = 1):
        super().__init__(linea, columna)
        self.nombre = nombre

    def __repr__(self) -> str:
        return f"Id({self.nombre})"


def formatear_nodo_ast(nodo: NodoAST, prefijo: str = "", es_ultimo: bool = True) -> List[str]:
    """
    Genera lineas jerarquicas en caracteres de dibujo para representar el AST.
    """
    lineas: List[str] = []
    conector = "└── " if es_ultimo else "├── "

    if isinstance(nodo, NodoPrograma):
        lineas.append(f"{prefijo}{conector}Programa ({len(nodo.sentencias)} sentencias)")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        total = len(nodo.sentencias)
        for i, s in enumerate(nodo.sentencias):
            lineas.extend(formatear_nodo_ast(s, nuevo_prefijo, i == total - 1))

    elif isinstance(nodo, NodoAsignacion):
        lineas.append(f"{prefijo}{conector}Asignacion: '{nodo.variable}'")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.expresion, nuevo_prefijo, True))

    elif isinstance(nodo, NodoPrint):
        lineas.append(f"{prefijo}{conector}Print")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.expresion, nuevo_prefijo, True))

    elif isinstance(nodo, NodoEvaluacionExpresion):
        lineas.append(f"{prefijo}{conector}Evaluar Expresion")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.expresion, nuevo_prefijo, True))

    elif isinstance(nodo, NodoBinario):
        lineas.append(f"{prefijo}{conector}Operador Binario: '{nodo.operador}'")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.izq, nuevo_prefijo, False))
        lineas.extend(formatear_nodo_ast(nodo.der, nuevo_prefijo, True))

    elif isinstance(nodo, NodoUnario):
        lineas.append(f"{prefijo}{conector}Operador Unario: '{nodo.operador}'")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.operando, nuevo_prefijo, True))

    elif isinstance(nodo, NodoFuncion):
        lineas.append(f"{prefijo}{conector}Funcion Matematica: {nodo.nombre}()")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        lineas.extend(formatear_nodo_ast(nodo.argumento, nuevo_prefijo, True))

    elif isinstance(nodo, NodoNumero):
        lineas.append(f"{prefijo}{conector}Numero: {nodo.valor}")

    elif isinstance(nodo, NodoIdentificador):
        lineas.append(f"{prefijo}{conector}Identificador: '{nodo.nombre}'")

    else:
        lineas.append(f"{prefijo}{conector}{repr(nodo)}")

    return lineas


def arbol_ast_a_texto(nodo: NodoAST) -> str:
    """Convierte un arbol AST a una representacion jerarquica estructurada en texto."""
    return "\n".join(formatear_nodo_ast(nodo, "", True))
