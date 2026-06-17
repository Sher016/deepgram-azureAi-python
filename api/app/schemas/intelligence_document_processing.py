from pydantic import BaseModel
 
 
class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
 
 
class IdpResponse(BaseModel):
    request_id: str
    document_type: str
    azure_model: str
    extracted_data: dict
    token_usage: TokenUsage
    
#no se si Faltaria agregar el formato en el que deben devolver los datos extraidos del documento en un json como lo piden