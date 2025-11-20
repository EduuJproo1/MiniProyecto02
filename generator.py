import random
import json

class GeneradorCasos:
    def __init__(self, archivo_gramatica):
        self.gramatica = {}
        self.simbolo_inicial = None
        self.cargar_gramatica(archivo_gramatica)

    def cargar_gramatica(self, archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line: continue 
                
                if "->" in line:
                    partes = line.split("->")
                else:
                    print(f"Advertencia: Línea ignorada: {line}")
                    continue

                cabeza = partes[0].strip()
                cuerpo = partes[1].strip()
                tokens = cuerpo.split()
                
                if cabeza not in self.gramatica:
                    self.gramatica[cabeza] = []
                    if self.simbolo_inicial is None:
                        self.simbolo_inicial = cabeza
                
                self.gramatica[cabeza].append(tokens)
            print(f"Gramática cargada. Inicial: {self.simbolo_inicial}")
            
        except FileNotFoundError:
            print("Error: No se encontró el archivo de gramática.")
            raise  # Re-lanzamos el error para que la GUI lo detecte

    def es_no_terminal(self, simbolo):
        return simbolo in self.gramatica

    def generar_caso_valido(self, profundidad_max=5):
        return self._derivacion(self.simbolo_inicial, 0, profundidad_max)

    def _derivacion(self, simbolo, profundidad_actual, profundidad_max):
        if not self.es_no_terminal(simbolo):
            if simbolo == 'numero': return str(random.randint(1, 99))
            if simbolo == 'id': return random.choice(['a', 'b', 'x', 'y', 'count', 'val'])
            return simbolo

        reglas_posibles = self.gramatica[simbolo]
        
        if profundidad_actual >= profundidad_max:
            reglas_posibles = sorted(reglas_posibles, key=len)[:1]
        
        regla_elegida = random.choice(reglas_posibles)
        
        resultado = []
        for token in regla_elegida:
            fragmento = self._derivacion(token, profundidad_actual + 1, profundidad_max)
            resultado.append(fragmento)
            
        return " ".join(resultado)

    def generar_caso_invalido(self, profundidad_max=5):
        cadena_valida = self.generar_caso_valido(profundidad_max)
        tokens = cadena_valida.split()
        
        if len(tokens) < 2: 
            return cadena_valida + " +", "Operador sin operando (final)"

        tipo_error = random.choice(["eliminar", "duplicar", "intercambiar", "caracter_ilegal"])
        tokens_mutados = tokens[:] 
        descripcion = ""

        if tipo_error == "eliminar":
            idx = random.randint(0, len(tokens_mutados) - 1)
            eliminado = tokens_mutados.pop(idx)
            descripcion = f"Eliminación de token '{eliminado}'"
        elif tipo_error == "duplicar":
            idx = random.randint(0, len(tokens_mutados) - 1)
            simbolo = tokens_mutados[idx]
            tokens_mutados.insert(idx, simbolo)
            descripcion = f"Duplicación de token '{simbolo}'"
        elif tipo_error == "intercambiar":
            idx = random.randint(0, len(tokens_mutados) - 2)
            tokens_mutados[idx], tokens_mutados[idx+1] = tokens_mutados[idx+1], tokens_mutados[idx]
            descripcion = f"Intercambio entre '{tokens_mutados[idx+1]}' y '{tokens_mutados[idx]}'"
        elif tipo_error == "caracter_ilegal":
            idx = random.randint(0, len(tokens_mutados))
            simbolo_ilegal = random.choice(['@', '#', '$', '?', 'INVALID'])
            tokens_mutados.insert(idx, simbolo_ilegal)
            descripcion = f"Inserción de caracter ilegal '{simbolo_ilegal}'"

        return " ".join(tokens_mutados), descripcion

    def generar_caso_extremo(self, profundidad_objetivo=15):
        return self._derivacion_extrema(self.simbolo_inicial, 0, profundidad_objetivo)

    def _derivacion_extrema(self, simbolo, profundidad_actual, profundidad_objetivo):
        if not self.es_no_terminal(simbolo):
            if simbolo == 'numero': return str(random.randint(1000, 9999))
            if simbolo == 'id': return random.choice(['var_long', 'count_max', 'total_sum'])
            return simbolo

        reglas_posibles = self.gramatica[simbolo]
        
        if profundidad_actual < profundidad_objetivo:
            reglas_expansivas = [r for r in reglas_posibles if any(self.es_no_terminal(t) for t in r)]
            if reglas_expansivas:
                reglas_expansivas.sort(key=len, reverse=True)
                regla_elegida = reglas_expansivas[0]
            else:
                regla_elegida = random.choice(reglas_posibles)
        else:
            regla_elegida = min(reglas_posibles, key=len)

        resultado = []
        for token in regla_elegida:
            fragmento = self._derivacion_extrema(token, profundidad_actual + 1, profundidad_objetivo)
            resultado.append(fragmento)
            
        return " ".join(resultado)