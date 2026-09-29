"""
Evaluador Semantico del Arbol de Sintaxis Abstracta (AST).
Valida tipos, variables inicializadas y evalua operaciones matematicas.
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

import math
from typing import List, Union, Optional
from dataclasses import dataclass, field
from .tabla_simbolos import TablaSimbolos, ErrorSemantico
from sintactico.arbol_sintactico import (
    NodoAST, NodoPrograma, NodoSentencia, NodoAsignacion, NodoPrint,
    NodoEvaluacionExpresion, NodoExpr, NodoBinario, NodoUnario,
    NodoFuncion, NodoNumero, NodoIdentificador
)


@dataclass
class RegistroPasoSemantico:
    tipo_accion: str
    descripcion: str
    resultado: Optional[Union[int, float]] = None


@dataclass
class ResultadoEjecucion:
    exito: bool
    salidas_impresion: List[str] = field(default_factory=list)
    errores_semanticos: List[str] = field(default_factory=list)
    tabla_simbolos: Optional[TablaSimbolos] = None
    pasos_ejecucion: List[RegistroPasoSemantico] = field(default_factory=list)

    @property
    def pasos(self) -> List[RegistroPasoSemantico]:
        return self.pasos_ejecucion


class EvaluadorSemantico:
    """
    Recorre el AST ejecutando las comprobaciones semanticas y calculando los valores finales.
    """

    def __init__(self, tabla_simbolos: Optional[TablaSimbolos] = None):
        self.tabla_simbolos = tabla_simbolos or TablaSimbolos()
        self.salidas_impresion: List[str] = []
        self.errores: List[str] = []
        self.pasos: List[RegistroPasoSemantico] = []

    def ejecutar_programa(self, ast: NodoPrograma) -> ResultadoEjecucion:
        self.salidas_impresion.clear()
        self.errores.clear()
        self.pasos.clear()

        for sentencia in ast.sentencias:
            try:
                self._ejecutar_sentencia(sentencia)
            except ErrorSemantico as err:
                self.errores.append(str(err))
            except ZeroDivisionError:
                self.errores.append("Error semantico: Division o modulo por cero.")
            except Exception as err:
                self.errores.append(f"Error semantico en ejecucion: {err}")

        exito = len(self.errores) == 0
        return ResultadoEjecucion(
            exito=exito,
            salidas_impresion=list(self.salidas_impresion),
            errores_semanticos=list(self.errores),
            tabla_simbolos=self.tabla_simbolos,
            pasos_ejecucion=list(self.pasos)
        )

    def _ejecutar_sentencia(self, sentencia: NodoSentencia):
        if isinstance(sentencia, NodoAsignacion):
            valor = self._evaluar_expr(sentencia.expresion)
            simb = self.tabla_simbolos.asignar(
                sentencia.variable,
                valor,
                sentencia.linea,
                sentencia.columna
            )
            self.pasos.append(RegistroPasoSemantico(
                tipo_accion="Asignacion",
                descripcion=f"{sentencia.variable} = {self._formatear_numero(valor)}",
                resultado=valor
            ))

        elif isinstance(sentencia, NodoPrint):
            valor = self._evaluar_expr(sentencia.expresion)
            val_str = self._formatear_numero(valor)
            self.salidas_impresion.append(val_str)
            self.pasos.append(RegistroPasoSemantico(
                tipo_accion="Impresion",
                descripcion=f"print({val_str})",
                resultado=valor
            ))

        elif isinstance(sentencia, NodoEvaluacionExpresion):
            valor = self._evaluar_expr(sentencia.expresion)
            self.pasos.append(RegistroPasoSemantico(
                tipo_accion="Evaluacion",
                descripcion=f"Expr => {self._formatear_numero(valor)}",
                resultado=valor
            ))

    def _evaluar_expr(self, expr: NodoExpr) -> Union[int, float]:
        if isinstance(expr, NodoNumero):
            return expr.valor

        elif isinstance(expr, NodoIdentificador):
            return self.tabla_simbolos.obtener(expr.nombre, expr.linea, expr.columna)

        elif isinstance(expr, NodoUnario):
            val_operando = self._evaluar_expr(expr.operando)
            if expr.operador == '-':
                return -val_operando
            raise ErrorSemantico(f"Operador unario no soportado: '{expr.operador}'", expr.linea, expr.columna)

        elif isinstance(expr, NodoFuncion):
            val_arg = self._evaluar_expr(expr.argumento)
            fn_nom = expr.nombre.lower()

            if fn_nom == 'abs':
                return abs(val_arg)
            elif fn_nom == 'sin':
                return math.sin(val_arg)
            elif fn_nom == 'cos':
                return math.cos(val_arg)
            elif fn_nom == 'tan':
                # Validar asintota de tangente (cos(x) cercano a 0)
                if abs(math.cos(val_arg)) < 1e-12:
                    raise ErrorSemantico(f"Indeterminacion matematica en tan({val_arg}): division por cero en asintota", expr.linea, expr.columna)
                return math.tan(val_arg)
            elif fn_nom in ('sqrt', 'raiz'):
                # Validar dominio de la funcion en el cuerpo de los numeros reales (x >= 0)
                if val_arg < 0:
                    raise ErrorSemantico(f"Error semantico: Raiz cuadrada de un numero negativo ({val_arg}). No definida en los numeros reales.", expr.linea, expr.columna)
                return math.sqrt(val_arg)
            else:
                raise ErrorSemantico(f"Funcion matematica desconocida: '{expr.nombre}'", expr.linea, expr.columna)

        elif isinstance(expr, NodoBinario):
            val_izq = self._evaluar_expr(expr.izq)
            val_der = self._evaluar_expr(expr.der)
            op = expr.operador

            if op == '+':
                return val_izq + val_der
            elif op == '-':
                return val_izq - val_der
            elif op == '*':
                return val_izq * val_der
            elif op == '/':
                if val_der == 0:
                    raise ErrorSemantico("Error semantico: Division por cero.", expr.linea, expr.columna)
                return val_izq / val_der
            elif op == '%':
                if val_der == 0:
                    raise ErrorSemantico("Error semantico: Operacion modulo por cero.", expr.linea, expr.columna)
                return val_izq % val_der
            else:
                raise ErrorSemantico(f"Operador binario desconocido: '{op}'", expr.linea, expr.columna)

        raise ErrorSemantico("Nodo de expresion no reconocido en el evaluador", expr.linea, expr.columna)

    @staticmethod
    def _formatear_numero(valor: Union[int, float]) -> str:
        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))
        if isinstance(valor, float):
            return f"{valor:.6f}".rstrip("0").rstrip(".")
        return str(valor)
