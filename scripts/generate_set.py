import sys
from pathlib import Path
import json

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from questions.question_generation import QuestionGenerator
from questions.config import DATA_DIR
from questions.question_generation import MCQuestion
from questions.bcba_outline import TOPICS
import random

def generate_questions_batch(question_generator: QuestionGenerator, num_questions: int, domain: str=None, subdomain: str=None, difficulty: str=None) -> list:
    """Generate a batch of questions.
    
    Args:
        question_generator: QuestionGenerator instance
        num_questions: Number of questions to generate
        domain: Optional specific domain
        subdomain: Optional specific subdomain
        difficulty: Optional specific difficulty level
    
    Returns:
        list: List of generated questions
    """
    questions = []
    for i in range(num_questions):
        print(f"Generating question {i+1} of {num_questions}")
        if domain is None:
            current_domain = random.choice(list(TOPICS.keys()))
        else:
            current_domain = domain
            
        if difficulty is None:
            current_difficulty = random.choice(["easy", "medium", "hard"])
        else:
            current_difficulty = difficulty
            
        question = question_generator.generate_question(
            domain=current_domain, 
            subdomain=subdomain, 
            difficulty=current_difficulty
        )
        questions.append(question)
    
    return questions

def save_questions_batch(questions: list, file_name: str):
    """Save a batch of questions to a json file, appending if file exists.
    
    Args:
        questions: List of MCQuestion objects
        file_name: Name of the file to save to
    """
    file_path = Path(DATA_DIR, f"{file_name}")
    
    # Convert questions to dicts
    questions_data = []
    for question in questions:
        question_dict = {
            "id": question.id,
            "question": question.question,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "rationale": question.rationale,
            "domain": question.domain,
            "subdomain": question.subdomain,
            "difficulty": question.difficulty,
            "model_params": question.model_params,
            "prompts": question.prompts
        }
        questions_data.append(question_dict)
    
    # Load existing data if file exists
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []
    
    # Combine existing and new questions
    all_questions = existing_data + questions_data
    
    # Save all questions at once
    with open(file_path, "w") as f:
        json.dump(all_questions, f, indent=2)
    
    print(f"Saved {len(questions)} new questions to {file_path}")
    print(f"Total questions in file: {len(all_questions)}")
    
    return str(file_path)

def generate_set(question_generator: QuestionGenerator, num_questions: int, domain: str=None, subdomain: str=None, difficulty: str=None, file_name: str=None):
    """Generate a set of questions and save them to a json file."""
    if file_name is None:
        file_name = "question_set.json"
    
    # Generate all questions in batch
    questions = generate_questions_batch(
        question_generator=question_generator,
        num_questions=num_questions,
        domain=domain,
        subdomain=subdomain,
        difficulty=difficulty
    )
    
    # Save all questions at once
    save_questions_batch(questions, file_name)
    return

if __name__ == "__main__":
    question_generator = QuestionGenerator(
        model_name="gpt-4o-mini",
        temperature=0.5,
        max_tokens=1000
    )
    
    generate_set(
        question_generator=question_generator,
        num_questions=5,
        file_name="test_set.json"
    )