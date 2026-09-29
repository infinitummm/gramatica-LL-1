# Manual de Usuario del Lenguaje

**Asignatura:** Lenguajes de Programacion y Traduccion  
**Integrantes:** Dylan Torres · Juan Gomez · Javier Rosero  
**Repositorio:** [infinitummm/gramatica-LL-1](https://github.com/infinitummm/gramatica-LL-1)  

---

## 1. Reglas Generales del Lenguaje

- **Fin de sentencia:** Toda sentencia o instruccion debe finalizar obligatoriamente con punto y coma (`;`).
- **Mayusculas y minusculas:** Las palabras clave y funciones reservadas se deben escribir en minusculas (`print`, `abs`, `sin`, `cos`, `tan`, `sqrt`, `raiz`).
- **Espacios y saltos de linea:** Se emplean para separar elementos; no alteran la semantica del programa.
- **Comentarios:** Las lineas que inician con `#` se consideran comentarios y se ignoran por completo.
- **Variables e Identificadores:**
  - Los nombres de variables inician con una letra o guion bajo (`_`), seguidos de letras, digitos o guiones bajos.
  - Toda variable debe recibir un valor mediante asignacion antes de poder utilizarse en cualquier expresion.
- **Tipos de Datos Soportados:**
  - Numeros enteros (ejemplo: `0`, `15`, `-8`).
  - Numeros decimales (ejemplo: `3.141592653589793`, `12.5`, `99.45`).

---

## 2. Nombres Reservados y Funciones Disponibles

El lenguaje cuenta con las siguientes palabras reservadas y funciones predefinidas:

| Nombre | Sintaxis | Que Hace |
| :--- | :--- | :--- |
| `print` | `print(expresion);` | Imprime en pantalla el valor calculado de la expresion. |
| `abs` | `abs(expresion)` | Retorna el valor absoluto del numero o expresion dada. |
| `sin` | `sin(expresion)` | Retorna el seno trigonometrico del angulo recibido en radianes. |
| `cos` | `cos(expresion)` | Retorna el coseno trigonometrico del angulo recibido en radianes. |
| `tan` | `tan(expresion)` | Retorna la tangente trigonometrica del angulo recibido en radianes. Valida que no coincida con una asintota. |
| `sqrt` | `sqrt(expresion)` | Retorna la raiz cuadrada del argumento. Valida que el argumento sea mayor o igual a cero. |
| `raiz` | `raiz(expresion)` | Equivalente en espanol de `sqrt`. Retorna la raiz cuadrada de la expresion (requiere argumento mayor o igual a cero). |

---

## 3. Operadores Disponibles y Precedencia

Los operadores se evaluan en el siguiente orden de prioridad:

| Operador | Nombre | Tipo | Descripcion | Precedencia |
| :---: | :--- | :--- | :--- | :---: |
| `( )` | Parentesis | Delimitador | Agrupacion y alteracion de la prioridad aritmetica. | Nivel 1 (Mayor) |
| `-` | Negacion unaria | Unario | Cambia el signo del operando que le sigue (ejemplo: `-15`, `-(x + 2)`). | Nivel 2 |
| `*` | Multiplicacion | Binario | Multiplica dos valores numericos. | Nivel 3 |
| `/` | Division | Binario | Divide el operando izquierdo entre el derecho. Error si el divisor es cero. | Nivel 3 |
| `%` | Modulo | Binario | Obtiene el residuo de una division entera. Error si el divisor es cero. | Nivel 3 |
| `+` | Suma | Binario | Suma dos valores numericos. | Nivel 4 |
| `-` | Resta | Binario | Resta el operando derecho del izquierdo. | Nivel 4 |
| `=` | Asignacion | Sentencia | Asigna el valor resultante de una expresion a una variable. | Nivel 5 (Menor) |

*Asociatividad:* Los operadores binarios del mismo nivel (`*`, `/`, `%`) y (`+`, `-`) se evaluan de izquierda a derecha.

---

## 4. Estructura de las Sentencias

El lenguaje admite tres tipos de sentencias:

1. **Asignacion de variable:**
   ```text
   nombre_variable = expresion;
   ```

2. **Impresion de salida:**
   ```text
   print(expresion);
   ```

3. **Evaluacion de expresion directa:**
   ```text
   expresion;
   ```

---

## 5. Reglas Gramaticales del Lenguaje

Las construcciones del lenguaje se rigen formalmente por las siguientes reglas de produccion:

```text
P1:  Programa            -> ListaSentencias $
P2:  ListaSentencias     -> Sentencia ListaSentencias
P3:  ListaSentencias     -> ε
P4:  Sentencia           -> ID RestoID ;
P5:  Sentencia           -> PRINT ( Expr ) ;
P6:  Sentencia           -> ExprSinID ;
P7:  RestoID             -> = Expr
P8:  RestoID             -> TermSol ExprSol
P9:  ExprSinID           -> FactorSinID TermSol ExprSol
P10: Expr                -> Term ExprSol
P11: ExprSol             -> + Term ExprSol
P12: ExprSol             -> - Term ExprSol
P13: ExprSol             -> ε
P14: Term                -> Factor TermSol
P15: TermSol             -> * Factor TermSol
P16: TermSol             -> / Factor TermSol
P17: TermSol             -> % Factor TermSol
P18: TermSol             -> ε
P19: Factor              -> ID
P20: Factor              -> FactorSinID
P21: FactorSinID         -> NUM
P22: FactorSinID         -> ( Expr )
P23: FactorSinID         -> ABS ( Expr )
P24: FactorSinID         -> SIN ( Expr )
P25: FactorSinID         -> COS ( Expr )
P26: FactorSinID         -> TAN ( Expr )
P27: FactorSinID         -> SQRT ( Expr )
P28: FactorSinID         -> - Factor
```

---

## 6. Reglas de Validacion y Manejo de Errores

El lenguaje detecta de forma controlada las siguientes infracciones:

| Categoria | Causa | Ejemplo | Diagnostico Emitido |
| :--- | :--- | :--- | :--- |
| **Error Lexico** | Caracter que no pertenece al alfabeto del lenguaje. | `x = 50 @ 10;` | Caracter inesperado. |
| **Error Sintactico** | Omision del punto y coma final (`;`). | `a = 10 + 20` | Se esperaba terminal `;`. |
| **Error Sintactico** | Operadores yuxtapuestos o sintaxis incompleta. | `y = 15 + * 3;` | Token no esperado en la expresion. |
| **Error Semantico** | Uso de una variable no inicializada. | `b = no_existe + 5;` | Variable no ha sido declarada ni asignada previamente. |
| **Error Semantico** | Division por cero. | `res = 100 / 0;` | Error semantico: Division por cero. |
| **Error Semantico** | Operacion de modulo por cero. | `res = 50 % 0;` | Error semantico: Operacion modulo por cero. |
| **Error Semantico** | Raiz cuadrada con argumento negativo. | `r = sqrt(-25);` | Error semantico: Raiz cuadrada de un numero negativo. |
| **Error Semantico** | Tangente en un punto de asintota. | `t = tan(pi / 2);` | Indeterminacion matematica en asintota. |

---

## 7. Ejemplos de Codigo

```text
# Asignacion y calculos aritmeticos con precedencia
base = 12.5;
altura = 8.0;
area = (base * altura) / 2;
print(area);

# Raices cuadradas exactas y compuestas
raiz_exacta = sqrt(144);
raiz_pitagoras = raiz(3 * 3 + 4 * 4);
print(raiz_exacta);
print(raiz_pitagoras);

# Funciones trigonometricas y valor absoluto
pi = 3.141592653589793;
seno_90 = sin(pi / 2);
valor_positivo = abs(-99.45);
print(seno_90);
print(valor_positivo);
```
