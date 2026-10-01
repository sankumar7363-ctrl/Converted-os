from pydantic import BaseModel

from core.ai.status import AIAvailability


class AIProviderResult(BaseModel):

    status: AIAvailability
    model: object | None = None
    message: str | None = None
