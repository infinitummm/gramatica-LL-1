"""
Tabla de Simbolos para la gestion de identificadores y variables.
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class ErrorSemantico(Exception):
    def __init__(self, mensaje: str, linea: int = 1, columna: int = 1):
        super().__init__(f"Error semantico en linea {linea}, columna {columna}: {mensaje}")
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna


@dataclass
class Simbolo:
    nombre: str
    valor: Any
    tipo_dato: str
    linea_definicion: int
    columna_definicion: int


class TablaSimbolos:
    """
    Estructura de almacenamiento y consulta para variables del programa.
    Garantiza que no se utilicen variables no inicializadas.
    """

    def __init__(self):
        self._simbolos: Dict[str, Simbolo] = {}

    def asignar(self, nombre: str, valor: Any, linea: int, columna: int) -> Simbolo:
        tipo = "float" if isinstance(valor, float) else "int"
        simb = Simbolo(
            nombre=nombre,
            valor=valor,
            tipo_dato=tipo,
            linea_definicion=linea,
            columna_definicion=columna
        )
        self._simbolos[nombre] = simb
        return simb

    def obtener(self, nombre: str, linea: int, columna: int) -> Any:
        if nombre not in self._simbolos:
            raise ErrorSemantico(f"Variable '{nombre}' no ha sido declarada ni asignada previamente.", linea, columna)
        return self._simbolos[nombre].valor

    def contiene(self, nombre: str) -> bool:
        return nombre in self._simbolos

    def listar_simbolos(self) -> List[Simbolo]:
        return list(self._simbolos.values())

    def limpiar(self):
        self._simbolos.clear()

    def __repr__(self) -> str:
        items = [f"{k}={v.valor} ({v.tipo_dato})" for k, v in self._simbolos.items()]
        return "TablaSimbolos(" + ", ".join(items) + ")"
