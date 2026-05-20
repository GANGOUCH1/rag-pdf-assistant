import os
from urllib import response
import google.genai as genai
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
###lamam_index to load in PDF and to embed them.
# what we jsut did is we made a vector_db which allow us to upload essentially vectors and search for vectors.
## but the things is i still need  to create the vectors.
###
load_dotenv()

print("GEMINI KEY:", os.getenv("GEMINI_API_KEY"))  # add this line
### Setting the api_key and version explicitly
client = genai.Client(
    api_key=os.getenv("GEMA_API_KEY"),
)

EMBED_MODEL= "text-embedding-001"
## ther's all kind of models that can embed text for u. in this case we'r using
#EMBED_DIM = 3072 # we make sure the same dim in vectDB
EMBED_DIM=768  # text-embedding-004 is natively 768 dimensions
##EMBED_DIM = 768 in the vector DB, which is the most important thing —
# the model and the Qdrant collection dimension must always match.
splitter = SentenceSplitter(chunk_size = 1000, chunk_overlap = 200)
# 200 represents the caracter max is 500 caracter NOT A WORD  FOR EX my name is tim
## if we chunck to 1,  my name is  : is tim  chunck_overlap =1

# we cannot embed all the PDF instead what we need to do it , chunk
# chunk it break it down into smaller pieces, and then embed those smaller pieces

def load_and_chunk_pdf(path: str) -> list[str]:
#"""Loads a PDF file and breaks its contents into smaller text fragments."""
#"""Loads a PDF file using SimpleDirectoryReader and breaks it into chunks."""
    reader=SimpleDirectoryReader(input_file=[path])
    docs = reader.load_data()
# Extract raw text from available documents
    texts = [d.text for d in docs if getattr(d, "text", None)]
### we gonna get all the text content for every single document inside our documents
### if this document, has some text attribute , because u might have a PDF THAT ONLY HAS Images for ex not text
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    #"""Generates numerical vector arrays from a list of strings using Gemini API.
   #    """Generates numerical vectors from text strings using the Gemini API.
    # Google GenAI natively supports batch embedding lists of strings
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
    )
    #Removed OpenAI references: Swapped out client.emedding.create (which followed an outdated OpenAI formatting pattern)
    # with Google's native client.models.embed_content()

    # Extract the float values out of the response structure
    return [item.values for item in response.embeddings]


