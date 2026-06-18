# deepgram azureAI implementation

## Consideraciones técnicas:

### Endpoints en ámbitos productivos
Pese a que la tarea pide endpoints inmediatos para la transcripción de audio, generación de texto o extracción estas operaciones pueden ser pesadas y tomar mucho tiempo de procesamiento (lo cual puede generar problemas de seguridad o estabilidad de servicios al tener diferentes conecciones abiertas al mismo tiempo). Por ende se propone endpoints adicionales tipo webhook con nombres de "better_way" en su nombre.

Así que los endpoints "better_way" devuelven el id del task y se sugiere que los servicios que consuman este hagan llamadas a los endpoints de consultas determinados en la documentación para conocer el estado de sus errores.

Como se puede observar en [resultados](./load_test/benchmark_results.csv) donde se satura la db y no da respuesta alguna.