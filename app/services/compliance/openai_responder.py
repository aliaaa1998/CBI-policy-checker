import json
from openai import OpenAI
from app.core.config import settings


class ResponseService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)

    def ask(self, instruction: str, payload: dict, schema: dict) -> dict:
        content = f"Instruction:\n{instruction}\n\nPayload:\n{json.dumps(payload, ensure_ascii=False)}"
        response = self.client.responses.create(
            model=settings.openai_response_model,
            input=content,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "policy_output",
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        return json.loads(response.output_text)
