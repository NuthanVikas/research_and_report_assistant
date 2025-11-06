import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def _get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env file or export it before using the LLM."
        )
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key


class LLMModel:
    """Simple wrapper to provide a configured OpenAI chat model."""

    def __init__(self, model_name: str = "gpt-4o"):
        if not model_name:
            raise ValueError("Model name must be provided.")

        _get_openai_api_key()
        self.model_name = model_name
        self._openai_model = ChatOpenAI(model=self.model_name)

    def get_model(self) -> ChatOpenAI:
        return self._openai_model


if __name__ == "__main__":
    llm_instance = LLMModel()
    llm_model = llm_instance.get_model()
    response = llm_model.invoke("hi")

    print(response)
