import os
from typing import Any, Optional

from .base_client import BaseLLMClient, normalize_content
from .validators import validate_model


class BedrockClient(BaseLLMClient):
    """Client for AWS Bedrock via ChatBedrockConverse.

    Authentication uses standard AWS credential chain (env vars, ~/.aws/credentials,
    instance profile). No API key required — configure via:
        AWS_REGION (or AWS_DEFAULT_REGION): Bedrock region
        AWS_PROFILE: optional named profile
    """

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)

    def get_llm(self) -> Any:
        """Return configured ChatBedrockConverse instance."""
        from langchain_aws import ChatBedrockConverse

        self.warn_if_unknown_model()

        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        llm_kwargs: dict[str, Any] = {
            "model_id": self.model,
            "region_name": region,
        }

        profile = os.environ.get("AWS_PROFILE")
        if profile:
            llm_kwargs["credentials_profile_name"] = profile

        for key in ("callbacks", "temperature", "max_tokens"):
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]

        return ChatBedrockConverse(**llm_kwargs)

    def validate_model(self) -> bool:
        """Validate model for bedrock provider."""
        return validate_model("bedrock", self.model)
