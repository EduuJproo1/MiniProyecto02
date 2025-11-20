import random
import json
import time
import datetime

class GeneradorCasos:
    def __init__(self, archivo_gramatica):
        self.gramatica = {}
        self.simbolo_inicial = None
        self.cargar_gramatica(archivo_gramatica)

    def cargar_gramatica(self, archivo):
        """Lee el archivo y convierte las reglas en un diccionario."""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line: continue # Saltar líneas vacías
                
                # Separar lado izquierdo (Cabeza) del derecho (Cuerpo)
                if "->" in line:
                    partes = line.split("->")
                else:
                    print(f"Advertencia: Línea con formato incorrecto ignorada: {line}")
                    continue

                cabeza = partes[0].strip()
                cuerpo = partes[1].strip()
                
                # Dividir el cuerpo en tokens (separados por espacio)
                tokens = cuerpo.split()
                
                # Guardar en el diccionario
                if cabeza not in self.gramatica:
                    self.gramatica[cabeza] = []
                    # El primer símbolo que leemos suele ser el inicial
                    if self.simbolo_inicial is None:
                        self.simbolo_inicial = cabeza
                
                self.gramatica[cabeza].append(tokens)
            
            print("✅ Gramática cargada exitosamente.")
            print(f"🔹 Símbolo inicial: {self.simbolo_inicial}")
            print(f"🔹 Reglas detectadas: {json.dumps(self.gramatica, indent=2)}")
            
        except FileNotFoundError:
            print("❌ Error: No se encontró el archivo de gramática.")

    def es_no_terminal(self, simbolo):
        """Verifica si un símbolo es una variable (tiene reglas asociadas)."""
        return simbolo in self.gramatica

    def generar_caso_valido(self, profundidad_max=5):
        """Método público para iniciar la generación."""
        # Iniciamos la recursión desde el símbolo inicial (ej: 'E')
        return self._derivacion(self.simbolo_inicial, 0, profundidad_max)

    def _derivacion(self, simbolo, profundidad_actual, profundidad_max):
        """
        Método recursivo núcleo.
        Retorna una cadena (string) con el fragmento generado.
        """
        # CASO BASE: Si es un terminal, lo devolvemos tal cual.
        if not self.es_no_terminal(simbolo):
            # Opcional: Reemplazar tokens genéricos por valores reales
            if simbolo == 'numero':
                return str(random.randint(1, 99)) # Genera un número real
            if simbolo == 'id':
                return random.choice(['a', 'b', 'x', 'y', 'count', 'val']) # Variable real
            return simbolo

        # ELEGIR REGLA:
        reglas_posibles = self.gramatica[simbolo]
        
        # Lógica de Control de Profundidad:
        # Si ya estamos muy profundo, intentamos elegir reglas que NO sean recursivas
        # para intentar terminar la cadena.
        if profundidad_actual >= profundidad_max:
            # Filtramos reglas que lleven rápido a terminales (heurística simple: las más cortas)
            reglas_posibles = sorted(reglas_posibles, key=len)[:1]
        
        # Elegimos una regla aleatoriamente de las permitidas
        regla_elegida = random.choice(reglas_posibles)
        
        resultado = []
        for token in regla_elegida:
            # Llamada recursiva para cada token de la regla
            fragmento = self._derivacion(token, profundidad_actual + 1, profundidad_max)
            resultado.append(fragmento)
            
        # Unimos todo con espacios
        return " ".join(resultado)

    # --- SECCIÓN MUTADOR (CASOS INVÁLIDOS) ---
    def generar_caso_invalido(self, profundidad_max=5):
        """
        Genera primero un caso válido y luego le aplica un error sintáctico.
        Retorna: (cadena_invalida, descripcion_del_error)
        """
        # 1. Obtenemos una cadena válida base
        cadena_valida = self.generar_caso_valido(profundidad_max)
        tokens = cadena_valida.split()
        
        if len(tokens) < 2: 
            # Si es muy corta, forzamos un error simple agregando algo ilegal
            return cadena_valida + " +", "Operador sin operando (final)"

        # 2. Elegimos un tipo de mutación aleatoria
        tipo_error = random.choice(["eliminar", "duplicar", "intercambiar", "caracter_ilegal"])
        
        tokens_mutados = tokens[:] # Copia de la lista
        descripcion = ""

        if tipo_error == "eliminar":
            # Eliminamos un token al azar
            idx = random.randint(0, len(tokens_mutados) - 1)
            eliminado = tokens_mutados.pop(idx)
            descripcion = f"Eliminación de token '{eliminado}'"

        elif tipo_error == "duplicar":
            # Duplicamos un operador o símbolo
            idx = random.randint(0, len(tokens_mutados) - 1)
            simbolo = tokens_mutados[idx]
            tokens_mutados.insert(idx, simbolo)
            descripcion = f"Duplicación de token '{simbolo}'"

        elif tipo_error == "intercambiar":
            # Intercambiamos dos tokens adyacentes
            idx = random.randint(0, len(tokens_mutados) - 2)
            tokens_mutados[idx], tokens_mutados[idx+1] = tokens_mutados[idx+1], tokens_mutados[idx]
            descripcion = f"Intercambio entre '{tokens_mutados[idx+1]}' y '{tokens_mutados[idx]}'"
            
        elif tipo_error == "caracter_ilegal":
            # Insertamos un símbolo que no existe en la gramática
            idx = random.randint(0, len(tokens_mutados))
            simbolo_ilegal = random.choice(['@', '#', '$', '?', 'INVALID'])
            tokens_mutados.insert(idx, simbolo_ilegal)
            descripcion = f"Inserción de caracter ilegal '{simbolo_ilegal}'"

        return " ".join(tokens_mutados), descripcion

    # --- SECCIÓN CASOS EXTREMOS ---
    def generar_caso_extremo(self, profundidad_objetivo=15):
        """
        Intenta generar la cadena más larga y profunda posible hasta llegar al objetivo.
        """
        return self._derivacion_extrema(self.simbolo_inicial, 0, profundidad_objetivo)

    def _derivacion_extrema(self, simbolo, profundidad_actual, profundidad_objetivo):
        # CASO BASE: Si es terminal, retornar valor
        if not self.es_no_terminal(simbolo):
            if simbolo == 'numero': return str(random.randint(1000, 9999)) # Números grandes
            if simbolo == 'id': return random.choice(['var_long', 'count_max', 'total_sum'])
            return simbolo

        reglas_posibles = self.gramatica[simbolo]
        
        # LÓGICA EXTREMA:
        # 1. Si aun no llegamos a la profundidad objetivo, FORZAMOS expansión.
        #    Filtramos reglas que tengan No Terminales (para seguir creciendo).
        if profundidad_actual < profundidad_objetivo:
            reglas_expansivas = [r for r in reglas_posibles if any(self.es_no_terminal(t) for t in r)]
            
            # Si existen reglas expansivas, elegimos la más larga de ellas
            if reglas_expansivas:
                # Ordenamos por longitud descendente (la más larga primero)
                reglas_expansivas.sort(key=len, reverse=True)
                # Elegimos una de las más largas (para variar un poco, tomamos de las top 2)
                regla_elegida = reglas_expansivas[0]
            else:
                regla_elegida = random.choice(reglas_posibles)
        else:
            # 2. Si llegamos al tope, cerramos rápido (igual que en validos)
            regla_elegida = min(reglas_posibles, key=len)

        resultado = []
        for token in regla_elegida:
            fragmento = self._derivacion_extrema(token, profundidad_actual + 1, profundidad_objetivo)
            resultado.append(fragmento)
            
        return " ".join(resultado)

class GestorPruebas:
    def __init__(self, generador):
        self.generador = generador
        self.resultados = []
        self.estadisticas = {
            "total_generado": 0,
            "por_categoria": {"valida": 0, "invalida": 0, "extrema": 0},
            "longitud_promedio": 0,
            "operadores_total": {"+": 0, "-": 0, "*": 0, "/": 0, "%": 0},
            "tiempo_total_ms": 0
        }

    def ejecutar_lote(self, n_validas, n_invalidas, n_extremas, config_profundidad):
        """
        Ejecuta la generación masiva y calcula métricas.
        """
        inicio = time.time()
        
        # 1. Generar Válidas
        for _ in range(n_validas):
            cadena = self.generador.generar_caso_valido(config_profundidad)
            self._registrar_caso("valida", cadena)

        # 2. Generar Inválidas
        for _ in range(n_invalidas):
            cadena, error = self.generador.generar_caso_invalido(config_profundidad)
            self._registrar_caso("invalida", cadena, info_extra=error)

        # 3. Generar Extremas
        for _ in range(n_extremas):
            # Para extremas usamos el doble de profundidad para que se note la diferencia
            cadena = self.generador.generar_caso_extremo(config_profundidad * 2)
            self._registrar_caso("extrema", cadena)

        fin = time.time()
        self.estadisticas["tiempo_total_ms"] = round((fin - inicio) * 1000, 2)
        self._calcular_promedios()

    def _registrar_caso(self, categoria, cadena, info_extra=""):
        """Guarda el caso individual y actualiza contadores en tiempo real."""
        tokens = cadena.split()
        longitud = len(tokens)
        
        # Contar operadores simples
        for token in tokens:
            if token in self.estadisticas["operadores_total"]:
                self.estadisticas["operadores_total"][token] += 1

        caso = {
            "id": self.estadisticas["total_generado"] + 1,
            "categoria": categoria,
            "cadena": cadena,
            "longitud": longitud,
            "detalle": info_extra
        }
        
        self.resultados.append(caso)
        self.estadisticas["total_generado"] += 1
        self.estadisticas["por_categoria"][categoria] += 1

    def _calcular_promedios(self):
        total_len = sum(c["longitud"] for c in self.resultados)
        if self.estadisticas["total_generado"] > 0:
            self.estadisticas["longitud_promedio"] = round(total_len / self.estadisticas["total_generado"], 2)

    def exportar_json(self, nombre_archivo="reporte_casos.json"):
        data_final = {
            "resumen_metricas": self.estadisticas,
            "casos_prueba": self.resultados
        }
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(data_final, f, indent=4, ensure_ascii=False)
            print(f"✅ Reporte exportado exitosamente a: {nombre_archivo}")
        except Exception as e:
            print(f"❌ Error al exportar JSON: {e}")

if __name__ == "__main__":
    # 1. Instanciar Generador
    gen = GeneradorCasos("gramatica.txt")
    
    # 2. Instanciar el Gestor de Pruebas
    gestor = GestorPruebas(gen)
    
    print("🚀 Iniciando generación por lotes...")
    
    # 3. Ejecutar un lote mixto
    # Pedimos: 50 válidas, 20 inválidas, 5 extremas. Profundidad base: 6
    gestor.ejecutar_lote(n_validas=50, n_invalidas=20, n_extremas=5, config_profundidad=6)
    
    # 4. Mostrar métricas en consola (resumen)
    stats = gestor.estadisticas
    print("\n--- REPORTE DE MÉTRICAS ---")
    print(f"Total de casos: {stats['total_generado']}")
    print(f"Tiempo ejecución: {stats['tiempo_total_ms']} ms")
    print(f"Longitud promedio: {stats['longitud_promedio']} tokens")
    print(f"Distribución: {stats['por_categoria']}")
    print(f"Operadores generados: {stats['operadores_total']}")
    
    # 5. Exportar a JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_json = f"resultado_pruebas_{timestamp}.json"
    gestor.exportar_json(nombre_json)