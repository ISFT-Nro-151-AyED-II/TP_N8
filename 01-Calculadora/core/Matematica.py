# el módulo re sirve para validar que la expresión solo contenga caracteres permitidos, evitando así 
# posibles inyecciones de código al usar eval().
import re

class MotorCalculadora:
    def __init__(self):
        # Permite solo números, puntos y operadores matemáticos básicos.
        # Decisión de diseño: Prevención de inyección de código en eval().
        self.patron_seguro = re.compile(r'^[0-9\.\+\-\*\/\(\)]+$')

    def resolver_expresion(self, expresion: str) -> str:
        if not expresion:
            return ""
            
        # Validación de input: Defensa contra caracteres no esperados.
        if not self.patron_seguro.match(expresion):
            return "Error: Input inválido"

        try:
            # Reemplazo de seguridad para evitar dobles operadores que rompan el parser.
            expresion_limpia = expresion.replace('++', '+').replace('--', '+')
            
            # Se usa eval de forma controlada porque el regex ya restringió el abanico de caracteres.
            resultado = eval(expresion_limpia)
            
            # Formateo: Si el resultado es entero, no mostrar el .0 para mayor legibilidad.
            if isinstance(resultado, float) and resultado.is_integer():
                return str(int(resultado))
            return str(round(resultado, 8)) # Límite de flotantes para evitar desbordes visuales.
            
        except ZeroDivisionError:
            return "Error: Div por 0"
        except SyntaxError:
            return "Error: Sintaxis"
        except Exception:
            return "Error"