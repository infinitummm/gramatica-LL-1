"""
Analizador Sintactico Predictivo LL(1).
Implementa la pila de derivacion basada en la tabla M[A, a] (Diapositivas 20 a 27)
y genera el Arbol de Sintaxis Abstracta (AST) para el analisis semantico.
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import List, Optional, Tuple, Dict, Any
from lexico.definicion_tokens import TipoToken, Token
from .gramatica_ll1 import GramaticaLL1, Produccion, EPSILON, FIN_ENTRADA
from .calculador_conjuntos import CalculadorConjuntosLL1
from .tabla_ll1 import TablaAnalisisLL1
from .arbol_sintactico import (
    NodoAST, NodoPrograma, NodoSentencia, NodoAsignacion, NodoPrint,
    NodoEvaluacionExpresion, NodoExpr, NodoBinario, NodoUnario,
    NodoFuncion, NodoNumero, NodoIdentificador
)


class ErrorSintactico(Exception):
    def __init__(self, mensaje: str, token: Token, esperados: Optional[List[str]] = None):
        super().__init__(f"Error sintactico en linea {token.linea}, columna {token.columna}: {mensaje}")
        self.token = token
        self.linea = token.linea
        self.columna = token.columna
        self.esperados = esperados or []


class AnalizadorSintacticoLL1:
    """
    Analizador LL(1) completo. Realiza:
    1. Verificacion de pertenencia formal mediante pila y tabla M[A, a].
    2. Construccion del Arbol de Sintaxis Abstracta (AST).
    3. Modo panico para recuperacion de errores usando conjuntos SIGUIENTES.
    """

    MAPA_TOKEN_A_TERMINAL: Dict[TipoToken, str] = {
        TipoToken.SUMA: '+',
        TipoToken.RESTA: '-',
        TipoToken.MULT: '*',
        TipoToken.DIV: '/',
        TipoToken.MOD: '%',
        TipoToken.ASIGNAR: '=',
        TipoToken.LPAREN: '(',
        TipoToken.RPAREN: ')',
        TipoToken.PUNTO_Y_COMA: ';',
        TipoToken.NUM: 'NUM',
        TipoToken.ID: 'ID',
        TipoToken.PRINT: 'PRINT',
        TipoToken.ABS: 'ABS',
        TipoToken.SIN: 'SIN',
        TipoToken.COS: 'COS',
        TipoToken.TAN: 'TAN',
        TipoToken.SQRT: 'SQRT',
        TipoToken.EOF: FIN_ENTRADA
    }

    def __init__(self, gramatica: Optional[GramaticaLL1] = None):
        self.gramatica = gramatica or GramaticaLL1()
        self.calculador = CalculadorConjuntosLL1(self.gramatica)
        self.tabla = TablaAnalisisLL1(self.gramatica, self.calculador)
        self.tokens: List[Token] = []
        self.indice = 0
        self.errores: List[ErrorSintactico] = []
        self.trazas_pila: List[Tuple[str, str, str]] = []

    def _token_actual(self) -> Token:
        if self.indice < len(self.tokens):
            return self.tokens[self.indice]
        return Token(TipoToken.EOF, "$", linea=1, columna=1)

    def _simbolo_terminal_actual(self) -> str:
        tok = self._token_actual()
        return self.MAPA_TOKEN_A_TERMINAL.get(tok.tipo, 'ERROR')

    def _avanzar(self) -> Token:
        tok = self._token_actual()
        if self.indice < len(self.tokens) - 1:
            self.indice += 1
        return tok

    def _emparejar(self, terminal_esperado: str) -> Token:
        simbolo_act = self._simbolo_terminal_actual()
        tok = self._token_actual()
        if simbolo_act == terminal_esperado:
            return self._avanzar()
        else:
            err = ErrorSintactico(
                f"Se esperaba terminal '{terminal_esperado}' pero se encontro '{tok.lexema}'",
                tok,
                [terminal_esperado]
            )
            self.errores.append(err)
            raise err

    # -------------------------------------------------------------------------
    # Ejecucion mediante Pila y Tabla M[A, a] (Algoritmo de la Diapositiva 21)
    # -------------------------------------------------------------------------

    def verificar_con_pila(self, tokens: List[Token]) -> bool:
        """
        Ejecuta el algoritmo clasico de analisis descendente no recursivo por tabla y pila.
        Retorna True si la cadena es aceptada por la gramatica LL(1).
        """
        self.tokens = [t for t in tokens if t.tipo != TipoToken.ERROR]
        self.indice = 0
        self.trazas_pila.clear()
        pila: List[str] = [FIN_ENTRADA, self.gramatica.SIMBOLO_INICIAL]

        while pila:
            cima = pila.pop()
            simbolo_act = self._simbolo_terminal_actual()
            tok_act = self._token_actual()

            estado_pila = " ".join(reversed(pila + [cima]))
            estado_entrada = " ".join(t.lexema for t in self.tokens[self.indice:self.indice + 5])

            if cima == FIN_ENTRADA:
                if simbolo_act == FIN_ENTRADA:
                    self.trazas_pila.append((estado_pila, estado_entrada, "Aceptar cadena"))
                    return True
                else:
                    self.trazas_pila.append((estado_pila, estado_entrada, "Error: Se esperaba fin de entrada"))
                    return False

            elif self.gramatica.es_terminal(cima):
                if cima == simbolo_act:
                    self.trazas_pila.append((estado_pila, estado_entrada, f"Emparejar terminal '{cima}'"))
                    self._avanzar()
                else:
                    self.trazas_pila.append((estado_pila, estado_entrada, f"Error: No coincide terminal '{cima}'"))
                    return False

            elif self.gramatica.es_no_terminal(cima):
                prod = self.tabla.obtener_produccion(cima, simbolo_act)
                if prod is not None:
                    self.trazas_pila.append((estado_pila, estado_entrada, f"Expandir {repr(prod)}"))
                    if prod.cuerpo != [EPSILON]:
                        for sym in reversed(prod.cuerpo):
                            pila.append(sym)
                else:
                    self.trazas_pila.append((estado_pila, estado_entrada, f"Error sintactico en M[{cima}, {simbolo_act}]"))
                    return False

        return False

    # -------------------------------------------------------------------------
    # Construccion del AST guiada por las decisiones de la Tabla LL(1)
    # -------------------------------------------------------------------------

    def analizar(self, tokens: List[Token]) -> Optional[NodoPrograma]:
        self.tokens = [t for t in tokens if t.tipo != TipoToken.ERROR]
        self.indice = 0
        self.errores.clear()

        try:
            ast = self._parse_programa()
            if self.errores:
                return None
            return ast
        except ErrorSintactico:
            return None

    def _parse_programa(self) -> NodoPrograma:
        sentencias = self._parse_lista_sentencias()
        self._emparejar(FIN_ENTRADA)
        return NodoPrograma(sentencias=sentencias)

    def _parse_lista_sentencias(self) -> List[NodoSentencia]:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('ListaSentencias', simbolo)

        if prod is None:
            self._error_panico('ListaSentencias', ['ID', 'PRINT', 'NUM', '(', 'ABS', 'SIN', 'COS', 'TAN', '-', ';', FIN_ENTRADA])
            return []

        if prod.cuerpo == [EPSILON]:
            return []

        # ListaSentencias -> Sentencia ListaSentencias
        sent = self._parse_sentencia()
        resto = self._parse_lista_sentencias()
        return [sent] + resto if sent else resto

    def _parse_sentencia(self) -> Optional[NodoSentencia]:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('Sentencia', simbolo)

        if prod is None:
            self._error_panico('Sentencia', ['ID', 'PRINT', 'NUM', '(', 'ABS', 'SIN', 'COS', 'TAN', '-'])
            return None

        primer_simbolo = prod.cuerpo[0]
        if primer_simbolo == 'ID':
            tok_id = self._emparejar('ID')
            nodo_resto = self._parse_resto_id(tok_id.lexema, tok_id.linea, tok_id.columna)
            self._emparejar(';')
            return nodo_resto

        elif primer_simbolo == 'PRINT':
            tok_print = self._emparejar('PRINT')
            self._emparejar('(')
            expr = self._parse_expr()
            self._emparejar(')')
            self._emparejar(';')
            return NodoPrint(expresion=expr, linea=tok_print.linea, columna=tok_print.columna)

        elif primer_simbolo == 'ExprSinID':
            expr = self._parse_expr_sin_id()
            self._emparejar(';')
            return NodoEvaluacionExpresion(expresion=expr, linea=expr.linea, columna=expr.columna)

        return None

    def _parse_resto_id(self, nombre_id: str, linea: int, columna: int) -> NodoSentencia:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('RestoID', simbolo)

        if prod is None:
            self._error_panico('RestoID', ['=', '*', '/', '%', '+', '-', ';'])
            return NodoAsignacion(variable=nombre_id, expresion=NodoNumero(0), linea=linea, columna=columna)

        if prod.cuerpo[0] == '=':
            self._emparejar('=')
            expr = self._parse_expr()
            return NodoAsignacion(variable=nombre_id, expresion=expr, linea=linea, columna=columna)
        else:
            # RestoID -> TermSol ExprSol
            nodo_id = NodoIdentificador(nombre=nombre_id, linea=linea, columna=columna)
            term_completo = self._parse_term_sol(nodo_id)
            expr_completa = self._parse_expr_sol(term_completo)
            return NodoEvaluacionExpresion(expresion=expr_completa, linea=linea, columna=columna)

    def _parse_expr_sin_id(self) -> NodoExpr:
        # ExprSinID -> FactorSinID TermSol ExprSol
        factor = self._parse_factor_sin_id()
        term = self._parse_term_sol(factor)
        return self._parse_expr_sol(term)

    def _parse_expr(self) -> NodoExpr:
        # Expr -> Term ExprSol
        term = self._parse_term()
        return self._parse_expr_sol(term)

    def _parse_expr_sol(self, izq: NodoExpr) -> NodoExpr:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('ExprSol', simbolo)

        if prod is None or prod.cuerpo == [EPSILON]:
            return izq

        operador = prod.cuerpo[0]
        if operador == '+':
            tok_op = self._emparejar('+')
            der = self._parse_term()
            nodo_binario = NodoBinario(operador='+', izq=izq, der=der, linea=tok_op.linea, columna=tok_op.columna)
            return self._parse_expr_sol(nodo_binario)
        elif operador == '-':
            tok_op = self._emparejar('-')
            der = self._parse_term()
            nodo_binario = NodoBinario(operador='-', izq=izq, der=der, linea=tok_op.linea, columna=tok_op.columna)
            return self._parse_expr_sol(nodo_binario)

        return izq

    def _parse_term(self) -> NodoExpr:
        # Term -> Factor TermSol
        factor = self._parse_factor()
        return self._parse_term_sol(factor)

    def _parse_term_sol(self, izq: NodoExpr) -> NodoExpr:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('TermSol', simbolo)

        if prod is None or prod.cuerpo == [EPSILON]:
            return izq

        operador = prod.cuerpo[0]
        if operador in ('*', '/', '%'):
            tok_op = self._emparejar(operador)
            der = self._parse_factor()
            nodo_binario = NodoBinario(operador=operador, izq=izq, der=der, linea=tok_op.linea, columna=tok_op.columna)
            return self._parse_term_sol(nodo_binario)

        return izq

    def _parse_factor(self) -> NodoExpr:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('Factor', simbolo)

        if prod is None:
            self._error_panico('Factor', ['ID', 'NUM', '(', 'ABS', 'SIN', 'COS', 'TAN', '-'])
            return NodoNumero(0)

        if prod.cuerpo[0] == 'ID':
            tok_id = self._emparejar('ID')
            return NodoIdentificador(nombre=tok_id.lexema, linea=tok_id.linea, columna=tok_id.columna)
        else:
            return self._parse_factor_sin_id()

    def _parse_factor_sin_id(self) -> NodoExpr:
        simbolo = self._simbolo_terminal_actual()
        prod = self.tabla.obtener_produccion('FactorSinID', simbolo)

        if prod is None:
            self._error_panico('FactorSinID', ['NUM', '(', 'ABS', 'SIN', 'COS', 'TAN', 'SQRT', '-'])
            return NodoNumero(0)

        primer_sym = prod.cuerpo[0]
        if primer_sym == 'NUM':
            tok = self._emparejar('NUM')
            return NodoNumero(valor=tok.valor, linea=tok.linea, columna=tok.columna)

        elif primer_sym == '(':
            self._emparejar('(')
            expr = self._parse_expr()
            self._emparejar(')')
            return expr

        elif primer_sym in ('ABS', 'SIN', 'COS', 'TAN', 'SQRT'):
            fn_tok = self._avanzar()
            fn_nombre = fn_tok.lexema.lower()
            self._emparejar('(')
            arg = self._parse_expr()
            self._emparejar(')')
            return NodoFuncion(nombre=fn_nombre, argumento=arg, linea=fn_tok.linea, columna=fn_tok.columna)

        elif primer_sym == '-':
            op_tok = self._emparejar('-')
            op_factor = self._parse_factor()
            return NodoUnario(operador='-', operando=op_factor, linea=op_tok.linea, columna=op_tok.columna)

        return NodoNumero(0)

    def _error_panico(self, no_terminal: str, esperados: List[str]):
        tok = self._token_actual()
        err = ErrorSintactico(f"Token no esperado '{tok.lexema}' en {no_terminal}", tok, esperados)
        self.errores.append(err)

        sincronizacion = self.calculador.siguientes_nt[no_terminal] | {';', FIN_ENTRADA}
        while self._simbolo_terminal_actual() not in sincronizacion and self._simbolo_terminal_actual() != FIN_ENTRADA:
            self._avanzar()
