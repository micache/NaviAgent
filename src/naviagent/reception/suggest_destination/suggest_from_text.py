import os
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import re

env_path = Path(__file__).resolve().parent.parent.parent.parent.parent / '.env'
# print(f"Loading from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

class TextDestinationAgent(Agent):
    """An agent that suggests destinations based on text input."""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")
        super().__init__(
            model=OpenAIChat(id=model, api_key=api_key),
            markdown=False
        )
    
    def suggest_destination(self, description: str):
        prompt = f'''
        Based on the following description, suggest a travel destination:
        "{description}"
        
        Only suggest well-known travel destinations in Vietnam and East/Southeast Asia.
        Provide the suggestion in JSON format: {{ 'destination': str, 'reason': str }}
        '''
        response = self.run(input=prompt, stream=False)
        
        response_text = response.content.strip()
        response_text = re.sub(r"```json|```", "", response_text).strip()
        
        return response_text

def get_destination_suggestion(description: str) -> str:
    agent = TextDestinationAgent()
    return agent.suggest_destination(description)

# def main():
#     agent = TextDestinationAgent()
#     description = input("Enter a description of your ideal travel destination: ")
#     # description = "A quiet place with flowers, pine trees, chilling temperature and supports recreational activities like hiking and camping."
#     result = agent.suggest_destination(description)
#     print("Suggested Destination:", result)

# if __name__ == "__main__":
#     main()