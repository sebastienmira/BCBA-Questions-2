import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.append(project_root)

from questions.bcba_outline import TOPICS

letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

topic_mapping = {
    key: letter for key,letter in zip(TOPICS.keys(), letters)
}
print(topic_mapping)