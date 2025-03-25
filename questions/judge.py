from questions.model import Model
from questions.question_generation import MCQuestion, get_prompt
from questions.bcba_outline import SUBDOMAINS

class Judge:
    def __init__(self):
        self.model = Model()
        
    def judge(self, question: MCQuestion) -> bool:
        system_prompt = get_prompt("judge/judge_system_prompt_1.txt")
        prompt = get_prompt("judge/judge_prompt_1.txt")
        subdomain = [SUBDOMAINS[subdomain] for subdomain in question.subdomain]
        prompt = prompt.format(question=question.question, options=question.options, correct_answer=question.correct_answer, rationale=question.rationale, domain=question.domain, subdomain=subdomain, cat_difficulty=question.cat_difficulty, bloom_taxonomy=question.bloom_taxonomy)
        
        evaluation = self.model.get_completion(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return evaluation