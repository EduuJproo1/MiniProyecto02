import time
import json

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
        inicio = time.time()
        
        # 1. Válidas
        for _ in range(n_validas):
            cadena = self.generador.generar_caso_valido(config_profundidad)
            self._registrar_caso("valida", cadena)

        # 2. Inválidas
        for _ in range(n_invalidas):
            cadena, error = self.generador.generar_caso_invalido(config_profundidad)
            self._registrar_caso("invalida", cadena, info_extra=error)

        # 3. Extremas
        for _ in range(n_extremas):
            # Usamos doble profundidad para que se note lo extremo
            cadena = self.generador.generar_caso_extremo(config_profundidad * 2)
            self._registrar_caso("extrema", cadena)

        fin = time.time()
        self.estadisticas["tiempo_total_ms"] = round((fin - inicio) * 1000, 2)
        self._calcular_promedios()

    def _registrar_caso(self, categoria, cadena, info_extra=""):
        tokens = cadena.split()
        longitud = len(tokens)
        
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
            print(f"Reporte exportado: {nombre_archivo}")
        except Exception as e:
            print(f"Error al exportar JSON: {e}")