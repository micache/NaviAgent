import os
import re
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from google.cloud import vision

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
print(f"Loading from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")


class DuckDuckGoImagesAgent(Agent):
    """An agent that can search for images using DuckDuckGo."""

    def __init__(self):
        super().__init__(
            model=OpenAIChat(id="gpt-4o-mini", api_key=api_key),
            tools=[DuckDuckGoTools()],
            markdown=False,
        )

    def search_image_location(self, image_url: str):
        prompt = """
        Find the location shown in this image and provide a brief description.
        Return in JSON format { 'location': str, 'description': str } with any additional details.
        """
        response = self.run(input=prompt, images=[Image(url=image_url)], stream=False)

        response_text = response.content.strip()
        response_text = re.sub(r"```json|```", "", response_text).strip()

        return response_text


class GoogleVisionImagesAgent(Agent):
    """An agent that can analyze images using Google Vision API."""

    def __init__(self):
        super().__init__(model=OpenAIChat(id="gpt-4o-mini", api_key=api_key), markdown=False)
        self.credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.client = vision.ImageAnnotatorClient()
        self.geolocator = Nominatim(user_agent="location_finder")

    def get_landmark_info(self, image_url: str) -> list:
        image = vision.Image()
        image.source.image_uri = image_url

        try:
            response = self.client.landmark_detection(image=image)
            return response.landmark_annotations
        except Exception as e:
            print(f"Error occurred: {e}")
            return []

    def get_detail_location(self, lat_lng):
        location = self.geolocator.reverse(
            (lat_lng.latitude, lat_lng.longitude), exactly_one=True, language="en"
        )
        return location.address

    def search_image_location(self, image_url: str):
        if not image_url:
            return "No image URL provided."

        landmarks = self.get_landmark_info(image_url)

        if not landmarks:
            return "No landmarks detected."

        landmark = landmarks[0]
        lat_lng = landmark.locations[0].lat_lng

        prompt = f"Provide a brief description of the landmark: {landmark.description}"
        response = self.run(input=prompt, stream=False)

        result = {"location": landmark.description, "description": response.content.strip()}

        return result


def main():
    # image_url = input("Enter the image URL: ")
    image_url = "https://www.civitatis.com/f/corea-del-sur/seul/entrada-torre-seul-grid.jpg"
    # agent = DuckDuckGoImagesAgent()
    agent = GoogleVisionImagesAgent()
    result = agent.search_image_location(image_url)
    print("Result:", result)


if __name__ == "__main__":
    main()
