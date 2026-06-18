# Pruebas de Carga y Rendimiento (Mocked)

Este directorio contiene las herramientas para realizar pruebas de carga a los endpoints de la API, comparando la estrategia normal vs `better_way`.

## Archivos

- `patched_app.py`: Levanta la aplicación FastAPI con parches (mocks) sobre los servicios de OpenAI y Deepgram para simular procesamiento (0.5s) sin consumir la API real.
- `benchmark.py`: Script con `aiohttp` que bombardea la aplicación con miles de peticiones para medir el rendimiento, latencia y fallos.

## Requisitos Previos

Asegúrate de tener instaladas las dependencias, en especial `aiohttp` (ya agregada en `requirements.txt`).

## Cómo ejecutar

### 1. Iniciar la Base de Datos
La aplicación necesita PostgreSQL. Puedes levantar solo la base de datos usando el `compose.yml` de la raíz:
```bash
docker-compose up -d db
```
*(Asegúrate de que en el archivo `.env` el `POSTGRES_HOST` apunte a `localhost` o la IP de docker si corres la app fuera del contenedor).*

### 2. Levantar el Servidor Parcheado
En la raíz del proyecto, ejecuta el servidor mockeado:
```bash
python load_test/patched_app.py
```
El servidor se ejecutará en el puerto `8001`.

### 3. Ejecutar el Benchmark
En otra terminal, desde la raíz del proyecto, ejecuta el script de pruebas de carga:
```bash
python load_test/benchmark.py --type both --requests 1000 --concurrency 100
```

### Opciones de Benchmark
- `--type`: `normal`, `better_way`, o `both`
- `--requests`: Número total de peticiones a enviar
- `--concurrency`: Número de peticiones simultáneas (conexiones)

## ¿Qué esperar?

- **Normal**: Los endpoints como `/stt` retendrán la conexión HTTP abierta hasta que el background worker termine. Con alta concurrencia, Uvicorn o los recursos del sistema pueden agotarse, produciendo timeouts o una alta latencia.
- **Better Way**: Endpoints como `/stt/better_way` responden inmediatamente con un `task_id` y delegan la tarea. La latencia será de escasos milisegundos y la tasa de éxito (HTTP 200) se mantendrá perfecta sin importar la concurrencia masiva (ej. 1000 peticiones en 1-2 segundos).

### Resultados
Al finalizar la ejecución del script `benchmark.py`, los resultados se guardarán o anexarán automáticamente en un archivo `load_test/benchmark_results.csv` para facilitar su análisis en herramientas externas.
