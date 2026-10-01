from core.ai.model import AIModel


class TestAIModel(AIModel):

    def generate(self, prompt: str) -> str:

        print("[AI MODEL] Received prompt:")
        print(prompt)

        return """
{
    "goal": "Create a portfolio website",
    "steps": [
        {
            "description": "Create project folder",
            "reason": "Organize the website files"
        },
        {
            "description": "Create HTML file",
            "reason": "Define the webpage structure"
        },
        {
            "description": "Create CSS file",
            "reason": "Define the visual styling"
        },
        {
            "description": "Verify the website",
            "reason": "Confirm that the generated files are valid"
        }
    ]
}
"""
