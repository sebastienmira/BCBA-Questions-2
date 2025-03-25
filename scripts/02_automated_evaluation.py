import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
print(project_root)
sys.path.append(project_root)

from questions.judge import Judge
from questions.question_generation import MCQuestion, QuestionGenerator

#question_generator = QuestionGenerator(model_name="gpt-4o-mini", temperature=0.5)
#question = question_generator.generate_question(domain="E", difficulty="easy")
question = {
    "id": "ed33b1f3-04c5-4200-8a35-3e51b9af2291",
    "question": "Dr. Smith is conducting a study to understand the aggressive behavior in children with autism in a classroom setting. He collects data through direct observation and uses this data to develop interventions aimed at reducing aggression. In his report, he describes the aggressive behaviors, predicts future occurrences based on environmental triggers, and implements interventions that successfully reduce aggressive incidents. Which of the following best illustrates Dr. Smith's approach in terms of behavior analysis as a science?",
    "options": [
      "Dr. Smith's approach exemplifies the goals of behavior analysis by focusing on description, prediction, and control of behavior.",
      "Dr. Smith's approach is primarily philosophical, emphasizing selectionism and pragmatism in understanding behavior.",
      "Dr. Smith's approach is rooted in the experimental analysis of behavior, focusing solely on laboratory-based research.",
      "Dr. Smith's approach represents professional practice guided by behavior analysis, without scientific foundation."
    ],
    "correct_answer": 0,
    "rationale": "Dr. Smith's approach aligns with the goals of behavior analysis as a science, which include description (observing and detailing aggressive behaviors), prediction (identifying environmental triggers that predict aggression), and control (implementing interventions to reduce aggression). This reflects an application of A1, where the goals of behavior analysis are identified and applied in a practical setting. Option B is incorrect because it misinterprets the focus on philosophical assumptions without addressing the scientific goals. Option C is incorrect as it refers to laboratory research, which is not the focus in this applied setting. Option D is incorrect because it implies a lack of scientific foundation, which contradicts the systematic and data-driven approach described.",
    "domain": [
      "Behaviorism and Philosophical Foundations"
    ],
    "subdomain": [
      "A4",
      "A1",
      "A2"
    ],
    "cat_difficulty": "medium",
    "bloom_taxonomy": "Analyze",
    "ai_generated": True
  }
question = MCQuestion(**question)
print(question)
judge = Judge()
evaluation = judge.judge(question)
print(evaluation)