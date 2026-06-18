# deepgram azureAI implementation

## Consideraciones técnicas:

### Endpoints en ámbitos productivos
Pese a que la tarea pide endpoints inmediatos para la transcripción de audio, generación de texto o extracción estas operaciones pueden ser pesadas y tomar mucho tiempo de procesamiento (lo cual puede generar problemas de seguridad o estabilidad de servicios al tener diferentes conecciones abiertas al mismo tiempo). Por ende se propone endpoints adicionales tipo webhook con nombres de "better_way" en su nombre.

Así que los endpoints "better_way" devuelven el id del task y se sugiere que los servicios que consuman este hagan llamadas a los endpoints de consultas determinados en la documentación para conocer el estado de sus errores.

Como se puede observar en [resultados](./load_test/benchmark_results.csv) donde se satura la db y no da respuesta alguna.

# Uso de la aplicación

Se debe clonar el repositorio y ubicarse en la carpeta clonada.

Además, requiere tener los puertos 8000 y 5434 disponibles para levantar la aplicación y la base de datos respectivamente.

## Requisitos previos
    docker

## Levantar la aplicación

    cd ./infra

Luego se construye las imágenes necesarias para levantar la aplicación:

    docker compose build

Finalmente, se levanta la aplicación:

    docker compose up

Todos los endpoints de la API requieren autenticación mediante una API Key. Esta debe enviarse en el header de cada request de la siguiente manera:

    API-Key: tu_api_key_aqui

Para consultar la documentación y uso de endpoints se puede consular una vez que la aplicación esté levantada en:

    http://localhost:8000/docs
