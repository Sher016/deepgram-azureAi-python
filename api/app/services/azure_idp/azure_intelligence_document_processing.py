import base64
import json
from pydantic import BaseModel

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.exceptions import ExternalServiceError, handle_external_errors
from app.schemas.intelligence_document_processing import IdResponseFormat
from app.services.llm.prompts.system_prompt import SYSTEM_PROMPT   
from app.services.llm.prompts.user_prompt import USER_PROMPT      
from app.services.base import DocumentProcessingService
from app.utils.file_utils import resolve_content_type

class AzureIDPService(DocumentProcessingService):
    """
    Receives any LangChain-compatible LLM via constructor injection.
    Swapping provider = swapping what you pass in, nothing here changes.
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    @handle_external_errors(service_name="Azure OpenAI")
    async def analyze(self, image_bytes: bytes, filename: str) -> dict:
        """
        Analyze a document image using Azure OpenAI Vision.
        """
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        media_type = resolve_content_type(filename, default="image/jpeg")

        structured_llm = self._llm.with_structured_output(IdResponseFormat, include_raw=True)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT), 
            HumanMessage(content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_b64}",
                        "detail": "high",
                    },
                },
                {"type": "text", "text": USER_PROMPT},  
            ]),
        ]

        response:dict = await structured_llm.ainvoke(messages)

        raw_response: AIMessage = response["raw"]
        model_response = response["parsed"]
        usage = raw_response.usage_metadata

        return {
            "document_type": "cedula",
            "extracted_data": model_response.model_dump(),
            "azure_model": raw_response.response_metadata.get("model_name", ""),
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }