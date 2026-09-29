"""
Definicion formal de la Gramatica LL(1) para el lenguaje matematico y de asignacion.
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from dataclasses import dataclass
from typing import List, Dict, Set


EPSILON = 'ε'
FIN_ENTRADA = '$'


@dataclass
class Produccion:
    id_prod: int
    no_terminal: str
    cuerpo: List[str]

    def __repr__(self) -> str:
        cuerpo_str = " ".join(self.cuerpo) if self.cuerpo != [EPSILON] else EPSILON
        return f"P{self.id_prod}: {self.no_terminal} -> {cuerpo_str}"


class GramaticaLL1:
    """
    Especificacion formal de los simbolos no terminales, terminales y producciones
    disenadas estrategicamente para cumplir con la condicion LL(1).
    """

    SIMBOLO_INICIAL = 'Programa'

    NO_TERMINALES: List[str] = [
        'Programa',
        'ListaSentencias',
        'Sentencia',
        'RestoID',
        'ExprSinID',
        'Expr',
        'ExprSol',
        'Term',
        'TermSol',
        'Factor',
        'FactorSinID'
    ]

    TERMINALES: List[str] = [
        '+', '-', '*', '/', '%', '=',
        '(', ')', ';',
        'NUM', 'ID',
        'PRINT', 'ABS', 'SIN', 'COS', 'TAN', 'SQRT',
        FIN_ENTRADA
    ]

    def __init__(self):
        self.producciones: List[Produccion] = []
        self._construir_producciones()
        self.mapa_producciones: Dict[str, List[Produccion]] = {}
        for p in self.producciones:
            self.mapa_producciones.setdefault(p.no_terminal, []).append(p)

    def _construir_producciones(self):
        lista = [
            # Programa
            ('Programa', ['ListaSentencias', FIN_ENTRADA]),

            # ListaSentencias
            ('ListaSentencias', ['Sentencia', 'ListaSentencias']),
            ('ListaSentencias', [EPSILON]),

            # Sentencia
            ('Sentencia', ['ID', 'RestoID', ';']),
            ('Sentencia', ['PRINT', '(', 'Expr', ')', ';']),
            ('Sentencia', ['ExprSinID', ';']),

            # RestoID (Permite discriminar asignacion vs expresion a partir de ID)
            ('RestoID', ['=', 'Expr']),
            ('RestoID', ['TermSol', 'ExprSol']),

            # ExprSinID
            ('ExprSinID', ['FactorSinID', 'TermSol', 'ExprSol']),

            # Expresiones aditivas (precedencia menor, asociativas a izquierda factorizadas)
            ('Expr', ['Term', 'ExprSol']),
            ('ExprSol', ['+', 'Term', 'ExprSol']),
            ('ExprSol', ['-', 'Term', 'ExprSol']),
            ('ExprSol', [EPSILON]),

            # Terminos multiplicativos y modulo (precedencia intermedia)
            ('Term', ['Factor', 'TermSol']),
            ('TermSol', ['*', 'Factor', 'TermSol']),
            ('TermSol', ['/', 'Factor', 'TermSol']),
            ('TermSol', ['%', 'Factor', 'TermSol']),
            ('TermSol', [EPSILON]),

            # Factores (unidades atomicas y funciones)
            ('Factor', ['ID']),
            ('Factor', ['FactorSinID']),

            # FactorSinID (numeros, parentesis, funciones matematicas y unario)
            ('FactorSinID', ['NUM']),
            ('FactorSinID', ['(', 'Expr', ')']),
            ('FactorSinID', ['ABS', '(', 'Expr', ')']),
            ('FactorSinID', ['SIN', '(', 'Expr', ')']),
            ('FactorSinID', ['COS', '(', 'Expr', ')']),
            ('FactorSinID', ['TAN', '(', 'Expr', ')']),
            ('FactorSinID', ['SQRT', '(', 'Expr', ')']),
            ('FactorSinID', ['-', 'Factor'])
        ]

        for idx, (nt, cuerpo) in enumerate(lista, start=1):
            self.producciones.append(Produccion(idx, nt, cuerpo))

    def es_terminal(self, simbolo: str) -> bool:
        return simbolo in self.TERMINALES

    def es_no_terminal(self, simbolo: str) -> bool:
        return simbolo in self.NO_TERMINALES
