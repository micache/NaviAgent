import os
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import re
from reception.suggest_destination.retrieval import RetrievalSystem
from reception.suggest_destination.config.config import config

env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
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
    
    def advanced_suggest_destination(self, description: str):
        # initialize retrieval system
        retrieval_system = RetrievalSystem()
        retrieval_system.create_collection(collection_name=config.index.collection_name)
        
        # retrieve relevant destinations
        results = retrieval_system.search(description, k=config.search.top_k, group_by_destination=config.search.group_by_destination)
        print("Retrieved Results:", results)
        
        # run LLM with retrieved results
        results_text = str(results)
        prompt = f'''
        You are a travel expert. Based on the following description and retrieved similar destinations, suggest a travel destination:
        Description: "{description}"
        Retrieved Destinations: {results_text}
        Prioritize destinations with higher ranking/similarity scores unless the description does not match well (such as the user wants to visit mountainous areas but the results with high confidence refers to beaches).
        If none of the retrieved destinations match well, you may suggest another suitable destination based on the description.
        Select ONLY ONE most relevant destination from the retrieved results that best matches the description. You may refine the description to better fit the retrieved destinations.
        Provide the suggestion in JSON format: {{ 'destination': str, 'reason': str }}
        '''
        response = self.run(input=prompt, stream=False)
        
        response_text = response.content.strip()
        response_text = re.sub(r"```json|```", "", response_text).strip()
        
        return response_text

def get_destination_suggestion(description: str) -> str:
    agent = TextDestinationAgent()
    return agent.advanced_suggest_destination(description)

# def main():
#     agent = TextDestinationAgent()
#     # description = input("Enter a description of your ideal travel destination: ")
#     description = "A quiet place with flowers, pine trees, chilling temperature and supports recreational activities like hiking and camping."
#     # description = 'Nơi nào đó nhiều đồi núi, có khí hậu mát mẻ, rừng thông và hoa, có thể đi dạo, chụp hình và thưởng thức ẩm thực địa phương.'
#     result = agent.advanced_suggest_destination(description)
#     print("Suggested Destination:", result)

# if __name__ == "__main__":
#     main()