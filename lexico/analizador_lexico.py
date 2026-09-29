"""
Analizador Lexico (Scanner) para el lenguaje LL(1).
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import List
from .definicion_tokens import TipoToken, Token


class ErrorLexico(Exception):
    def __init__(self, mensaje: str, linea: int, columna: int, caracter: str):
        super().__init__(f"Error lexico en linea {linea}, columna {columna}: {mensaje} (caracter '{caracter}')")
        self.linea = linea
        self.columna = columna
        self.caracter = caracter


class AnalizadorLexico:
    PALABRAS_RESERVADAS = {
        'print': TipoToken.PRINT,
        'abs': TipoToken.ABS,
        'sin': TipoToken.SIN,
        'cos': TipoToken.COS,
        'tan': TipoToken.TAN,
        'sqrt': TipoToken.SQRT,
        'raiz': TipoToken.SQRT
    }

    def __init__(self, fuente: str):
        self.fuente = fuente
        self.posicion = 0
        self.longitud = len(fuente)
        self.linea = 1
        self.columna = 1
        self.errores: List[ErrorLexico] = []

    def _caracter_actual(self) -> str:
        if self.posicion >= self.longitud:
            return '\0'
        return self.fuente[self.posicion]

    def _avanzar(self) -> str:
        ch = self._caracter_actual()
        self.posicion += 1
        if ch == '\n':
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return ch

    def _mirar_siguiente(self) -> str:
        if self.posicion + 1 >= self.longitud:
            return '\0'
        return self.fuente[self.posicion + 1]

    def escanear_tokens(self) -> List[Token]:
        tokens: List[Token] = []
        while self.posicion < self.longitud:
            ch = self._caracter_actual()

            # Omitir espacios en blanco y tabulaciones
            if ch in ' \t\r\n':
                self._avanzar()
                continue

            # Omitir comentarios de una linea (# o //)
            if ch == '#' or (ch == '/' and self._mirar_siguiente() == '/'):
                while self._caracter_actual() not in ('\n', '\0'):
                    self._avanzar()
                continue

            col_inicio = self.columna
            lin_inicio = self.linea

            # Numeros enteros y decimales
            if ch.isdigit():
                lexema = ""
                es_decimal = False
                while self._caracter_actual().isdigit():
                    lexema += self._avanzar()
                if self._caracter_actual() == '.' and self._mirar_siguiente().isdigit():
                    es_decimal = True
                    lexema += self._avanzar()
                    while self._caracter_actual().isdigit():
                        lexema += self._avanzar()
                val = float(lexema) if es_decimal else int(lexema)
                tokens.append(Token(TipoToken.NUM, lexema, valor=val, linea=lin_inicio, columna=col_inicio))
                continue

            # Identificadores y palabras reservadas
            if ch.isalpha() or ch == '_':
                lexema = ""
                while self._caracter_actual().isalnum() or self._caracter_actual() == '_':
                    lexema += self._avanzar()
                tipo = self.PALABRAS_RESERVADAS.get(lexema.lower(), TipoToken.ID)
                tokens.append(Token(tipo, lexema, valor=lexema if tipo == TipoToken.ID else None, linea=lin_inicio, columna=col_inicio))
                continue

            # Operadores y delimitadores individuales
            self._avanzar()
            if ch == '+':
                tokens.append(Token(TipoToken.SUMA, '+', linea=lin_inicio, columna=col_inicio))
            elif ch == '-':
                tokens.append(Token(TipoToken.RESTA, '-', linea=lin_inicio, columna=col_inicio))
            elif ch == '*':
                tokens.append(Token(TipoToken.MULT, '*', linea=lin_inicio, columna=col_inicio))
            elif ch == '/':
                tokens.append(Token(TipoToken.DIV, '/', linea=lin_inicio, columna=col_inicio))
            elif ch == '%':
                tokens.append(Token(TipoToken.MOD, '%', linea=lin_inicio, columna=col_inicio))
            elif ch == '=':
                tokens.append(Token(TipoToken.ASIGNAR, '=', linea=lin_inicio, columna=col_inicio))
            elif ch == '(':
                tokens.append(Token(TipoToken.LPAREN, '(', linea=lin_inicio, columna=col_inicio))
            elif ch == ')':
                tokens.append(Token(TipoToken.RPAREN, ')', linea=lin_inicio, columna=col_inicio))
            elif ch == ';':
                tokens.append(Token(TipoToken.PUNTO_Y_COMA, ';', linea=lin_inicio, columna=col_inicio))
            else:
                err = ErrorLexico("Caracter inesperado", lin_inicio, col_inicio, ch)
                self.errores.append(err)
                tokens.append(Token(TipoToken.ERROR, ch, linea=lin_inicio, columna=col_inicio))

        tokens.append(Token(TipoToken.EOF, "$", linea=self.linea, columna=self.columna))
        return tokens
