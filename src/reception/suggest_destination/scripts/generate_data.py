# %%
from openai import OpenAI
import time
import re
import csv
import pandas as pd
from tqdm import tqdm
import json
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
key = user_secrets.get_secret("OPENAI_KEY")

client = OpenAI(api_key=key)

# %%
import json

BATCH_FILE = "batch_input.jsonl"
PROMPT = """
Generate 20 travel samples in a strict JSON array. Output only JSON.

Each item must follow this format:
{
  "description": "...",
  "destination": "City, Country"
}

DESCRIPTION REQUIREMENTS:
- Write 1–2 sentences.
- Must NOT contain any city names, country names, or any explicit place names.
- Must describe a place as if it belongs to Vietnam, Japan, South Korea, China, Taiwan, Hong Kong, or Macau.
- Must be detailed and vivid: include sensory descriptions such as sounds, smells, textures, lighting, food scenes, weather, atmosphere, or surrounding architecture.
- Must reflect realistic elements of East Asian and Vietnamese environments. Examples of allowed elements:
    * Lantern-lit alleys, busy food stalls, steaming noodles, sizzling grills  
    * Traditional wooden houses, shrines, stone pathways, blossom-filled streets  
    * Night markets with bright signs, crowded vendor rows, fragrant snacks  
    * Misty mountains, terraced rice fields, bamboo forests, clear coastal waters  
    * Dense urban neighborhoods, neon-lit streets, narrow alleys with cafes  
    * Fishing boats, piers, coastal breezes, markets near the harbor
- Must feel culturally grounded, realistic, and region-appropriate — not generic.
- Every description MUST be unique, concrete, and specific in imagery.
- NO generic clichés like “beautiful scenery” or “a wonderful place.”
- NO stories, no characters, no time-related events.
- Description must describe the *environment*, not a narrative.

DESTINATION REQUIREMENTS:
- Must choose ONE value from the following list EXACTLY (case-sensitive):
[
  "Hanoi, Vietnam", "Ho Chi Minh City, Vietnam", "Da Nang, Vietnam", "Nha Trang, Vietnam",
  "Hoi An, Vietnam", "Hue, Vietnam", "Ha Long, Vietnam", "Sapa, Vietnam",
  "Phu Quoc, Vietnam", "Da Lat, Vietnam",

  "Beijing, China", "Shanghai, China", "Shenzhen, China", "Guangzhou, China",
  "Chengdu, China", "Hangzhou, China", "Xian, China", "Guilin, China",
  "Suzhou, China", "Kunming, China",

  "Tokyo, Japan", "Osaka, Japan", "Kyoto, Japan", "Sapporo, Japan",
  "Fukuoka, Japan", "Nagasaki, Japan", "Nara, Japan", "Yokohama, Japan",
  "Kobe, Japan",

  "Seoul, South Korea", "Busan, South Korea", "Incheon, South Korea",
  "Daegu, South Korea", "Jeju City, South Korea", "Gwangju, South Korea",

  "Taipei, Taiwan", "Taichung, Taiwan", "Kaohsiung, Taiwan", "Tainan, Taiwan",
  "Hualien, Taiwan",

  "Hong Kong, China", "Macau, China"
]

RESPONSE FORMAT:
Return ONLY a JSON array of exactly 20 objects with no extra text before or after.
"""

# Generate ~500 jobs for 10k samples
num_requests = 500

with open(BATCH_FILE, "w", encoding="utf-8") as f:
    for i in range(num_requests):
        job = {
            "custom_id": f"req-{i}",
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": "gpt-4o-mini",
                "input": PROMPT
            }
        }
        f.write(json.dumps(job) + "\n")

print("DONE:", BATCH_FILE)

# %%
# Upload batch file
batch_file = client.files.create(
    file=open("batch_input.jsonl", "rb"),
    purpose="batch"
)

# Create batch job
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/responses",
    completion_window="24h"
)

print("Batch ID:", batch.id)

# %%
batch = client.batches.retrieve(batch.id)
print(batch.status)

# Replace this entire cell with this working code:

from openai import OpenAI
import time
import json
import pandas as pd

# --- WAIT FOR BATCH TO COMPLETE ---
while True:
    batch = client.batches.retrieve(batch.id)
    print("Status:", batch.status)

    if batch.status == "completed":
        break
    elif batch.status in ["failed", "expired", "cancelled"]:
        raise RuntimeError(f"Batch stopped with status: {batch.status}")

    time.sleep(2)

# %%
output_file_id = batch.output_file_id
print("Output file id:", output_file_id)

file_response = client.files.content(output_file_id)

# ✔ file_response.text is the JSONL content
raw_text = file_response.text

# Save JSONL directly as UTF-8 text
with open("batch_output.jsonl", "w", encoding="utf-8") as f:
    f.write(raw_text)

print("Saved batch_output.jsonl successfully!")

# %%
rows = []

with open("batch_output.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        content = obj["response"]["output"][0]["content"][0]["text"]
        items = json.loads(content)
        rows.extend(items)

pd.DataFrame(rows).to_csv("travel_dataset_10k.csv", index=False)
print("DONE → travel_dataset_10k.csv")


