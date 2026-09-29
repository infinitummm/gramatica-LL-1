"""
Construccion y representacion tabular de la Tabla de Analisis Predictivo LL(1) M[A, a].
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import Dict, Optional, List
from .gramatica_ll1 import GramaticaLL1, Produccion
from .calculador_conjuntos import CalculadorConjuntosLL1


class TablaAnalisisLL1:
    """
    Construye la matriz de analisis predictivo M[A, a] a partir de los conjuntos PRED (Diapositivas 20 y 21).
    """

    def __init__(self, gramatica: GramaticaLL1, calculador: CalculadorConjuntosLL1):
        self.gramatica = gramatica
        self.calculador = calculador
        self.tabla: Dict[str, Dict[str, Optional[Produccion]]] = {}
        self._construir_tabla()

    def _construir_tabla(self):
        for nt in self.gramatica.NO_TERMINALES:
            self.tabla[nt] = {t: None for t in self.gramatica.TERMINALES}

        for prod in self.gramatica.producciones:
            nt = prod.no_terminal
            prediccion = self.calculador.prediccion_prod[prod.id_prod]

            for terminal in prediccion:
                if terminal in self.tabla[nt] and self.tabla[nt][terminal] is not None:
                    prod_existente = self.tabla[nt][terminal]
                    if prod_existente.id_prod != prod.id_prod:
                        # Conflicto LL(1) detectado
                        pass
                self.tabla[nt][terminal] = prod

    def obtener_produccion(self, no_terminal: str, terminal: str) -> Optional[Produccion]:
        if no_terminal in self.tabla and terminal in self.tabla[no_terminal]:
            return self.tabla[no_terminal][terminal]
        return None

    def generar_reporte_conjuntos(self) -> str:
        lineas = []
        lineas.append("=" * 80)
        lineas.append("CONJUNTOS PRIMEROS Y SIGUIENTES")
        lineas.append("=" * 80)
        lineas.append(f"{'No Terminal':<20} | {'PRIMEROS':<30} | {'SIGUIENTES':<24}")
        lineas.append("-" * 80)

        for nt in self.gramatica.NO_TERMINALES:
            prim_str = "{" + ", ".join(sorted(self.calculador.primeros_nt[nt])) + "}"
            sig_str = "{" + ", ".join(sorted(self.calculador.siguientes_nt[nt])) + "}"
            lineas.append(f"{nt:<20} | {prim_str:<30} | {sig_str:<24}")

        lineas.append("\n" + "=" * 80)
        lineas.append("CONJUNTOS DE PREDICCION (PRED) POR PRODUCCION")
        lineas.append("=" * 80)
        for prod in self.gramatica.producciones:
            pred_set = self.calculador.prediccion_prod[prod.id_prod]
            pred_str = "{" + ", ".join(sorted(pred_set)) + "}"
            lineas.append(f"{repr(prod):<50} => PRED = {pred_str}")

        lineas.append("\n" + "=" * 80)
        if self.calculador.es_ll1:
            lineas.append("ESTADO DE LA GRAMATICA: Cumple estrictamente la condicion LL(1). Cero conflictos.")
        else:
            lineas.append(f"ADVERTENCIA: Se detectaron {len(self.calculador.conflictos_ll1)} conflictos LL(1).")
        lineas.append("=" * 80)

        return "\n".join(lineas)

    def generar_tabla_visual(self) -> str:
        terminales_ordenados = [t for t in self.gramatica.TERMINALES]
        lineas = []
        lineas.append("=" * 120)
        lineas.append("TABLA DE ANALISIS SINTACTICO PREDICTIVO M[A, a]")
        lineas.append("=" * 120)

        encabezado = f"{'No Terminal':<16} | " + " | ".join(f"{t:<5}" for t in terminales_ordenados)
        lineas.append(encabezado)
        lineas.append("-" * len(encabezado))

        for nt in self.gramatica.NO_TERMINALES:
            celdas = []
            for t in terminales_ordenados:
                prod = self.tabla[nt].get(t)
                if prod is not None:
                    celdas.append(f"P{prod.id_prod:<4}")
                else:
                    celdas.append("  -  ")
            lineas.append(f"{nt:<16} | " + " | ".join(celdas))

        lineas.append("=" * len(encabezado))
        return "\n".join(lineas)
