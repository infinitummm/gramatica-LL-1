"""
Definicion de tipos de tokens y estructura de datos Token.
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TipoToken(Enum):
    # Palabras clave y funciones matematicas
    PRINT = auto()
    ABS = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    SQRT = auto()

    # Operadores aritmeticos
    SUMA = auto()      # +
    RESTA = auto()     # -
    MULT = auto()      # *
    DIV = auto()       # /
    MOD = auto()       # %

    # Operador de asignacion
    ASIGNAR = auto()   # =

    # Delimitadores
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    PUNTO_Y_COMA = auto()  # ;

    # Literales e Identificadores
    NUM = auto()
    ID = auto()

    # Control
    EOF = auto()
    ERROR = auto()


@dataclass
class Token:
    tipo: TipoToken
    lexema: str
    valor: Optional[Any] = None
    linea: int = 1
    columna: int = 1

    def __repr__(self) -> str:
        if self.valor is not None:
            return f"Token({self.tipo.name}, '{self.lexema}', valor={self.valor}, pos={self.linea}:{self.columna})"
        return f"Token({self.tipo.name}, '{self.lexema}', pos={self.linea}:{self.columna})"
