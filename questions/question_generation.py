import sys
sys.path.append("..")
from questions.config import PROMPTS_DIR
from pathlib import Path
from questions.model import Model, OPENAIKeys
from questions.bcba_outline import TOPICS
import re
import uuid
from dataclasses import dataclass
from typing import List
import random
from questions.sample_learning_topics import get_learning_objectives
import json

def get_prompt(prompt_name: str) -> str:
    """Get a prompt from the prompts directory."""
    prompt_path = Path(PROMPTS_DIR, prompt_name)
    with open(prompt_path, "r") as file:
        return file.read()


@dataclass
class MCQuestion:
    """Represents a multiple choice question."""
    id: str  # Unique identifier for the question
    question: str
    options: List[str]
    correct_answer: int  # Index of the correct answer
    rationale: str
    domain: str
    subdomain: str
    cat_difficulty: str
    bloom_taxonomy: str
    ai_generated: bool

class QuestionGenerator:
    """Generates BCBA multiple choice questions using OpenAI API."""
    def __init__(self,
                model_name:str = "gpt-4o-mini",
                temperature:float = 0.0,
                max_tokens: int = 1000,
                prompts: dict = {"system_prompt":"system_prompt_0.txt", "user_prompts":"difficulty_prompts_1"},
                **kwargs):
        """Initialize the question generator.
        
        Args:
            prompts: A dictionary containing the system and user prompts
            model_name: The name of the OpenAI model to use
            temperature: The temperature of the model
            max_tokens: The maximum number of tokens in the response
        """
        self.model = Model()
        
        self.prompts = prompts
        self.system_prompt = get_prompt(prompts["system_prompt"])
        self.user_prompts = prompts["user_prompts"]
        self.model_params = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
    
    def generate_question(self, domain: str, difficulty: str = "medium") -> MCQuestion:
        """Generate a multiple choice question.
        
        Args:
            topic: The topic of the question
            difficulty: The difficulty level of the question
            
        Returns:
            A multiple choice question as a MCQuestion object
        """
        objectives = get_learning_objectives(main_domain = domain, difficulty = difficulty)
        domain = ", ".join(objectives["domains"])
        subdomain = ", ".join(objectives["subdomains"])
        learning_objective = ", ".join(objectives["objectives"].values())

        user_prompt_file = f"{self.user_prompts}/{difficulty}_prompt.txt"
        user_prompt = get_prompt(user_prompt_file)

        user_prompt = user_prompt.format(domain=domain, subdomain=subdomain, learning_objective=learning_objective)

        response = self.model.get_completion(
            **self.model_params,
            messages=[
                {OPENAIKeys.ROLE: "system", OPENAIKeys.CONTENT: self.system_prompt},
                {OPENAIKeys.ROLE: "user", OPENAIKeys.CONTENT: user_prompt}
            ]
        )

        return self.parse_response(response=response, domain=objectives["domains"], subdomain=objectives["subdomains"], difficulty=difficulty)
    
    def parse_response(self, response: str, domain: list[str], subdomain: list[str], difficulty: str) -> MCQuestion:
        """Parse the model's response into a structured MCQuestion object.
                   
        Returns:
            A MCQuestion object containing the parsed question data
        """
        clean_response = re.sub(r"^```\s*json\s*|```$", "", response.strip(), flags=re.IGNORECASE)
        response = json.loads(clean_response)
        question = response["question"]
        options = response["options"]
        correct_answer = response["correct_answer"]
        rationale = response["rationale"]
        bloom_taxonomy = response["bloom_taxonomy"]

        return MCQuestion(
            id=str(uuid.uuid4()),
            question=question,
            options=options,
            correct_answer=correct_answer,
            rationale=rationale,
            domain=domain,
            subdomain=subdomain,
            cat_difficulty=difficulty,
            bloom_taxonomy=bloom_taxonomy,
            ai_generated=True
        )