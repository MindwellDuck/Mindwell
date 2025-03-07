"""docstring"""

import ollama
from maybe_forest_vars import ROOT, QUESTION, MAYBE, YES, NO, WEAK, cognitive_forest

class CognitiveDistortionDetector:

    """Detect cognitive distortions"""
    def __init__(self, tree: dict[str, dict[str, str]], thought: str) -> None:
        self.tree: dict[str, dict[str, str]] = tree
        self.thought: str = thought

    def answer(self, question: str) -> str:
        '''docstring'''
        print(question, end=' ')
        response: str = ollama.chat(
            model='deepseek-r1:14b',
            messages=[{
                'role': 'system',
                'content': "Answer ONLY 'yes', 'no', or 'maybe' to this question."
            }, {
                'role': 'user',
                'content': f"Text: {self.thought}\nQuestion: {question}"
            }],
            options={'temperature': 0}
        )['message']['content']
        print(response)
        return response.split("</think>\n\n", 1)[1].lower()

    def traverse_tree(self, node: str) -> list[str]:
        """Call llama and get answer"""
        while node in self.tree:
            answer = self.answer(self.tree[node][QUESTION])
            match answer:
                case maybe if maybe == MAYBE:
                    return [
                        f'{WEAK} {distortion}'
                        for distortion in self.traverse_tree(self.tree[node][YES])
                    ] + self.traverse_tree(self.tree[node][NO])
                case yes if yes == YES:
                    return self.traverse_tree(self.tree[node][YES])
                case no if no == NO:
                    return self.traverse_tree(self.tree[node][NO])
                case _:
                    return ["WRONG"]
        return [node]

    def get_distortions(self) -> list[str]:
        """get_distortion"""
        current_distortions = self.traverse_tree(ROOT)
        print(current_distortions)
        return current_distortions

if __name__=="__main__":
    distortions: list[str] = []
    for current_tree in cognitive_forest.items():
        detector = CognitiveDistortionDetector(current_tree[1], "I am an idiot")
        distortions += detector.get_distortions()
    print(distortions)
