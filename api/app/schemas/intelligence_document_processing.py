from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class RequestIdResponse(BaseModel):
    task_id: str


class IdpResponse(BaseModel):
    request_id: str
    document_type: str
    azure_model: str
    extracted_data: dict
    token_usage: TokenUsage


class IdResponseFormat(BaseModel):
    nombre: str = Field(..., description="Nombre del ciudadano")
    apellidos: str = Field(..., description="Apellidos del ciudadano")
    numero: str = Field(..., description="Numero de identificación del ciudadano")
    fecha_nacimiento: str = Field(..., description="Fecha de nacimiento")
    lugar_de_nacimiento: str = Field(..., description="Lugar de nacimiento")
    fecha_de_expedicion: str = Field(..., description="Fecha de expedición del documento")
    sexo: str = Field(..., description="Sexo del ciudadano")
    estatura: str = Field(..., description="Estatura del ciudadano")
    tipo_sangre: str = Field(..., description="Tipo de sangre")