import os
from dotenv import load_dotenv
import google.genai as genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="test sentence",
)
print("Success:", response.embeddings[0].values[:5])


for model in client.models.list():
    print(model.name)
### to test the embed and the models versions :  uv run python test_embed.py