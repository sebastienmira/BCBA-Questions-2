import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
print(project_root)
sys.path.append(project_root)

from questions.judge import Judge
from questions.question_generation import MCQuestion, QuestionGenerator

question_generator = QuestionGenerator(model_name="gpt-4o-mini", temperature=0.5)
question = question_generator.generate_question(domain="E", difficulty="easy")
print(question)
judge = Judge()
evaluation = judge.judge(question)
print(evaluation)