import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from questions.config import DATA_DIR
from questions.question_generation import MCQuestion

with open(DATA_DIR / "bloom_shuffled_review_questions_part1.json", "r") as f:
    data = json.load(f)
with open(DATA_DIR / "bloom_shuffled_review_questions_part2.json", "r") as f:
    data.extend(json.load(f))
    

def convert_to_mcq(question: dict) -> MCQuestion:
    mcq = {}
    mcq["id"] = question["id"]
    mcq["question"] = question["question"]
    mcq["options"] = question["options"]
    mcq["correct_answer"] = question["correct_answer"]
    mcq["rationale"] = question["rationale"]
    mcq["domain"] = question["domain"]
    mcq["subdomain"] = question["subdomain"]
    mcq["cat_difficulty"] = question["difficulty"]
    mcq["bloom_taxonomy"] = question["bloom_taxonomy"]
    mcq["ai_generated"] = True if question["model_params"]["model"] != "expert" else False
    return mcq

mcqs = []

for question in data:
    mcq = convert_to_mcq(question)
    mcqs.append(mcq)

with open(DATA_DIR / "mcqs_reviews.json", "w") as f:
    json.dump(mcqs, f, indent=2)
