import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from questions.config import DATA_DIR
import json
from questions.judge import Judge
from questions.question_generation import MCQuestion

with open(DATA_DIR / "mcqs_reviews.json", "r") as f:
    mcqs = json.load(f)

reviews = []
judge = Judge()
for i, mcq in enumerate(mcqs[:10]):
    print(f"Evaluating question {i+1} of {len(mcqs)}")
    mcq = MCQuestion(**mcq)
    evaluation = judge.judge(mcq)
    print(evaluation)
    reviews.append(evaluation)

with open(DATA_DIR / "reviews_ai_generated_2.json", "w") as f:
    json.dump(reviews, f, indent=2)
