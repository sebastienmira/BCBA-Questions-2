from openai import OpenAI
from questions.config import get_settings

class OPENAIKeys(str):
    ROLE = "role"
    CONTENT = "content"
    ANSWER = "answer"
        
class Model:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI()
        self.openai_api_key = self.settings.OPENAI_API_KEY
        
    def get_completion(self, **kwargs) -> str:
        """Get a completion from the model."""
        response = self.client.chat.completions.create(
            **kwargs
        )
        return response.choices[0].message.content