USER_PROMPT = """Analiza la siguiente cédula en busca de la siguiente información y devuelve los resultados en formato estructurado:

- nombre: Nombre del ciudadano.
- apellidos: Apellidos del ciudadano.
- numero: Número de identificación del ciudadano.
- fecha_nacimiento: Fecha de nacimiento del ciudadano.
- lugar_de_nacimiento: Lugar de nacimiento del ciudadano.
- fecha_de_expedicion: Fecha de expedición del documento.
- sexo: Sexo del ciudadano.
- estatura: Estatura del ciudadano.
- tipo_sangre: Tipo de sangre del ciudadano.

Si algún campo no está presente o no puede determinarse con certeza, un 'N/A' para dicho campo.
"""