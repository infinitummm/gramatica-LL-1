"""
Calculador automatico de conjuntos PRIMEROS, SIGUIENTES y PREDICCION para Gramatica LL(1).
Algoritmos basados estrictamente en el punto fijo teorico (Diapositivas 10 a 21).
Integrantes: Dylan Torres, Juan Gomez, Javier Rosero
"""

from typing import Dict, Set, List, Tuple
from .gramatica_ll1 import GramaticaLL1, Produccion, EPSILON, FIN_ENTRADA


class CalculadorConjuntosLL1:
    def __init__(self, gramatica: GramaticaLL1):
        self.gramatica = gramatica
        self.primeros_nt: Dict[str, Set[str]] = {}
        self.siguientes_nt: Dict[str, Set[str]] = {}
        self.prediccion_prod: Dict[int, Set[str]] = {}
        self.conflictos_ll1: List[Tuple[str, str, Produccion, Produccion]] = []

        self.calcular_todos()

    def calcular_todos(self):
        self._calcular_primeros()
        self._calcular_siguientes()
        self._calcular_prediccion()
        self._verificar_condicion_ll1()

    def primeros_de_secuencia(self, secuencia: List[str]) -> Set[str]:
        """
        Calcula el conjunto PRIMEROS de una cadena de simbolos X_1 X_2 ... X_k.
        Reglas de la Diapositiva 11:
        1. Si X_1 es terminal, PRIMEROS = {X_1}.
        2. Se agrega PRIMEROS(X_1) - {ε}.
        3. Si ε in PRIMEROS(X_1), se continua con X_2, y asi sucesivamente.
        4. Si todos los X_i son anulables, se agrega ε.
        """
        if not secuencia or secuencia == [EPSILON]:
            return {EPSILON}

        resultado: Set[str] = set()
        todos_anulables = True

        for simbolo in secuencia:
            if simbolo == EPSILON:
                continue

            if self.gramatica.es_terminal(simbolo):
                resultado.add(simbolo)
                todos_anulables = False
                break
            elif self.gramatica.es_no_terminal(simbolo):
                primeros_simbolo = self.primeros_nt.get(simbolo, set())
                resultado.update(primeros_simbolo - {EPSILON})
                if EPSILON not in primeros_simbolo:
                    todos_anulables = False
                    break
            else:
                raise ValueError(f"Simbolo desconocido en la gramatica: {simbolo}")

        if todos_anulables:
            resultado.add(EPSILON)

        return resultado

    def _calcular_primeros(self):
        """
        Algoritmo de punto fijo para PRIMEROS (Diapositiva 14).
        """
        self.primeros_nt = {nt: set() for nt in self.gramatica.NO_TERMINALES}
        cambio = True

        while cambio:
            cambio = False
            for prod in self.gramatica.producciones:
                nt = prod.no_terminal
                cuerpo = prod.cuerpo

                if cuerpo == [EPSILON]:
                    if EPSILON not in self.primeros_nt[nt]:
                        self.primeros_nt[nt].add(EPSILON)
                        cambio = True
                else:
                    sec_primeros = self.primeros_de_secuencia(cuerpo)
                    tam_previo = len(self.primeros_nt[nt])
                    self.primeros_nt[nt].update(sec_primeros)
                    if len(self.primeros_nt[nt]) > tam_previo:
                        cambio = True

    def _calcular_siguientes(self):
        """
        Algoritmo de punto fijo para SIGUIENTES (Diapositiva 16).
        Reglas:
        1. Para cada produccion A -> α B β: agregar PRIMEROS(β) - {ε} a SIGUIENTES(B).
        2. Si β =>* ε o β esta vacia: agregar SIGUIENTES(A) a SIGUIENTES(B).
        3. Inicializar $ in SIGUIENTES(SimboloInicial).
        4. Repetir hasta alcanzar punto fijo. ε nunca pertenece a SIGUIENTES.
        """
        self.siguientes_nt = {nt: set() for nt in self.gramatica.NO_TERMINALES}
        self.siguientes_nt[self.gramatica.SIMBOLO_INICIAL].add(FIN_ENTRADA)

        cambio = True
        while cambio:
            cambio = False
            for prod in self.gramatica.producciones:
                A = prod.no_terminal
                cuerpo = prod.cuerpo

                if cuerpo == [EPSILON]:
                    continue

                for i, B in enumerate(cuerpo):
                    if not self.gramatica.es_no_terminal(B):
                        continue

                    beta = cuerpo[i + 1:]
                    primeros_beta = self.primeros_de_secuencia(beta)

                    tam_previo = len(self.siguientes_nt[B])
                    self.siguientes_nt[B].update(primeros_beta - {EPSILON})

                    if EPSILON in primeros_beta or len(beta) == 0:
                        self.siguientes_nt[B].update(self.siguientes_nt[A])

                    if len(self.siguientes_nt[B]) > tam_previo:
                        cambio = True

    def _calcular_prediccion(self):
        """
        Calculo de conjuntos PRED para cada produccion A -> α (Diapositiva 18).
        PRED(A -> α) =
            PRIMEROS(α) si ε not in PRIMEROS(α)
            (PRIMEROS(α) - {ε}) U SIGUIENTES(A) si ε in PRIMEROS(α)
        """
        self.prediccion_prod = {}
        for prod in self.gramatica.producciones:
            A = prod.no_terminal
            cuerpo = prod.cuerpo
            primeros_alfa = self.primeros_de_secuencia(cuerpo)

            if EPSILON not in primeros_alfa:
                pred = set(primeros_alfa)
            else:
                pred = (primeros_alfa - {EPSILON}) | self.siguientes_nt[A]

            self.prediccion_prod[prod.id_prod] = pred

    def _verificar_condicion_ll1(self):
        """
        Comprueba que para cada no terminal con multiples alternativas,
        los conjuntos PRED sean disjuntos a pares (Diapositiva 9 y 20).
        """
        self.conflictos_ll1 = []
        for nt, prods in self.gramatica.mapa_producciones.items():
            n = len(prods)
            for i in range(n):
                for j in range(i + 1, n):
                    p1 = prods[i]
                    p2 = prods[j]
                    pred1 = self.prediccion_prod[p1.id_prod]
                    pred2 = self.prediccion_prod[p2.id_prod]
                    interseccion = pred1 & pred2
                    for token_conflicto in interseccion:
                        self.conflictos_ll1.append((nt, token_conflicto, p1, p2))

    @property
    def es_ll1(self) -> bool:
        return len(self.conflictos_ll1) == 0
