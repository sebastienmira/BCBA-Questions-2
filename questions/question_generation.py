from questions.config import PROMPTS_DIR
from pathlib import Path
from questions.model import Model, OPENAIKeys
from questions.bcba_outline import TOPICS
import re
import uuid
from dataclasses import dataclass
from typing import List
import random


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
    difficulty: str
    model_params: dict
    prompts: dict

class QuestionGenerator:
    """Generates BCBA multiple choice questions using OpenAI API."""
    def __init__(self,
                model_name:str = "gpt-4o-mini",
                temperature:float = 0.0,
                max_tokens: int = 1000,
                prompts: dict = {"system_prompt":"system_prompt_0.txt", "user_prompts":"difficulty_prompts_0"},
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

    def get_learning_objectives(self, domain: str, subdomain: str = None, difficulty: str = "medium") -> dict:
        """Get learning objectives based on difficulty level and domain.
        
        Args:
            domain: The primary domain from BCBA topics
            subdomain: Optional specific subdomain code (e.g., "B1"). If None, randomly selected
            difficulty: Difficulty level determining number of learning objectives:
                      - "easy": 1 learning objective from specified domain
                      - "medium": 2-3 learning objectives from same domain
                      - "hard": learning objectives from 2 different domains
        
        Returns:
            dict: A dictionary containing:
                - 'domains': List of domains used
                - 'subdomains': List of subdomains used
                - 'objectives': Dictionary mapping subdomain codes to their learning objectives
        
        Raises:
            ValueError: If domain or subdomain is invalid
        """
        # Validate primary domain
        if domain not in TOPICS:
            raise ValueError(f"Invalid domain: {domain}\n"
                            f"Valid domains: {list(TOPICS.keys())}")
        
        # Initialize return structure
        result = {
            'domains': [domain],
            'subdomains': [],
            'objectives': {}
        }
        
        # Handle subdomain selection based on difficulty
        if difficulty.lower() == "easy":
            # For easy, get single subdomain
            if not subdomain:
                subdomain = random.choice(list(TOPICS[domain].keys()))
            elif subdomain not in TOPICS[domain]:
                raise ValueError(f"Invalid subdomain: {subdomain}\n"
                               f"Valid subdomains: {list(TOPICS[domain].keys())}")
            result['subdomains'] = [subdomain]
            result['objectives'][subdomain] = TOPICS[domain][subdomain]

        elif difficulty.lower() == "medium":
            # For medium, get 2-3 subdomains from same domain
            if not subdomain:
                # If no subdomain specified, randomly select 2-3 subdomains
                num_subdomains = random.randint(2, 3)
                selected_subdomains = random.sample(list(TOPICS[domain].keys()), num_subdomains)
            else:
                # If subdomain specified, validate and add 1-2 more
                if subdomain not in TOPICS[domain]:
                    raise ValueError(f"Invalid subdomain: {subdomain}\n"
                                   f"Valid subdomains: {list(TOPICS[domain].keys())}")
                available_subdomains = [s for s in TOPICS[domain].keys() if s != subdomain]
                additional_count = random.randint(1, 2)
                additional_subdomains = random.sample(available_subdomains, additional_count)
                selected_subdomains = [subdomain] + additional_subdomains
            
            result['subdomains'] = selected_subdomains
            result['objectives'].update({sub: TOPICS[domain][sub] for sub in selected_subdomains})

        elif difficulty.lower() == "hard":
            # For hard, get objectives from two domains
            # Get primary domain objective
            if not subdomain:
                subdomain = random.choice(list(TOPICS[domain].keys()))
            elif subdomain not in TOPICS[domain]:
                raise ValueError(f"Invalid subdomain: {subdomain}\n"
                               f"Valid subdomains: {list(TOPICS[domain].keys())}")
            
            # Get additional domain and its random subdomain
            available_domains = [d for d in TOPICS.keys() if d != domain]
            additional_domain = random.choice(available_domains)
            additional_subdomain = random.choice(list(TOPICS[additional_domain].keys()))
            
            result['domains'].append(additional_domain)
            result['subdomains'] = [subdomain, additional_subdomain]
            result['objectives'].update({
                subdomain: TOPICS[domain][subdomain],
                additional_subdomain: TOPICS[additional_domain][additional_subdomain]
            })
        
        else:
            raise ValueError(f"Invalid difficulty: {difficulty}\n"
                            f"Must be one of: ['easy', 'medium', 'hard']")
        
        return result
    
    def generate_question(self, domain: str, subdomain: str=None, difficulty: str = "medium") -> MCQuestion:
        """Generate a multiple choice question.
        
        Args:
            topic: The topic of the question
            difficulty: The difficulty level of the question
            
        Returns:
            A multiple choice question as a MCQuestion object
        """
        objectives = self.get_learning_objectives(domain, subdomain, difficulty)

        domain = objectives["domains"]
        subdomain = objectives["subdomains"]
        learning_objective = objectives["objectives"]

        user_prompt_file = f"{self.user_prompts}/{difficulty}_prompt.txt"
        user_prompt = get_prompt(user_prompt_file)
        user_prompt = user_prompt.format(domain=domain, subdomain=subdomain, learning_objective=learning_objective, difficulty=difficulty)

        response = self.model.get_completion(
            **self.model_params,
            messages=[
                {OPENAIKeys.ROLE: "system", OPENAIKeys.CONTENT: self.system_prompt},
                {OPENAIKeys.ROLE: "user", OPENAIKeys.CONTENT: user_prompt}
            ]
        )

        return self.parse_response(response=response, domain=domain, subdomain=subdomain, difficulty=difficulty, user_prompt_file=user_prompt_file)
    
    def parse_response(self, response: str, domain: str, subdomain: str, difficulty: str, user_prompt_file: str) -> MCQuestion:
        """Parse the model's response into a structured MCQuestion object.
        
        Args:
            response: Raw text response from the model
            
        Returns:
            A MCQuestion object containing the parsed question data
        """
        # Extract question
        question_match = re.search(r"Q: (.*?)(?=\nA:)", response, re.DOTALL)
        question = question_match.group(1).strip() if question_match else ""

        # Extract options
        options = []
        for opt in ["A:", "B:", "C:", "D:"]:
            opt_match = re.search(f"{opt} (.*?)(?=\n|$)", response)
            if opt_match:
                options.append(opt_match.group(1).strip())
        
        # Extract correct answer
        correct_match = re.search(r"Correct: ([ABCD])", response)
        if correct_match:
            correct_letter = correct_match.group(1)
            correct_answer = ord(correct_letter) - ord('A')
        
        # Extract rationale
        rationale_match = re.search(r"Rationale: (.*?)(?=\n|$)", response)
        rationale = rationale_match.group(1).strip() if rationale_match else "" 

        return MCQuestion(
            id=str(uuid.uuid4()),
            question=question,
            options=options,
            correct_answer=correct_answer,
            rationale=rationale,
            domain=domain,
            subdomain=subdomain,
            difficulty=difficulty,
            model_params = self.model_params,
            prompts = {"system_prompt":self.prompts["system_prompt"], "user_prompt":user_prompt_file}
        )