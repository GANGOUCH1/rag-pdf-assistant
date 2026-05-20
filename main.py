import logging
import uuid
import os

import inngest
import inngest.fast_api
from fastapi import FastAPI
from dotenv import load_dotenv
from inngest.experimental import ai

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGQueryResult, RAGSearchResult, RAGChunkAndSrc, RAGUpsertResult

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def  rag_ingest_pdf(ctx: inngest.Context):

    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, name=f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        QdrantStorage.upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult)

    return ingested.model_dump()
@inngest_client.create_function(
    fn_id="RAG: Query PDF",                                     # unique ID for this function inside Inngest dashboard
    trigger=inngest.TriggerEvent(event="rag/query_pdf")         # this function runs when the "rag/query_pdf" event is fired
)
async def rag_query_pdf(ctx: inngest.Context):                  # ctx carries the event data (question, top_k, etc.)

    def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]                  # convert the question into an embedding vector (list of floats)
        store = QdrantStorage()                                  # create a connection to the Qdrant vector database
        found = store.search(query_vec, top_k)                  # find the top_k most similar chunks to the question vector
        return RAGSearchResult(                                  # wrap results in a typed Pydantic model so Inngest can serialize it
            contexts=found["contexts"],                         # the actual text chunks retrieved from the PDF
            sources=found["sources"]                            # the source filenames/IDs those chunks came from
        )

    question = ctx.event.data["question"]                       # extract the question string from the incoming event payload
    top_k = int(ctx.event.data.get("top_k", 5))                # extract top_k from payload, default to 5 if not provided

    found = await ctx.step.run(                                 # run _search as a tracked Inngest step (retryable, logged)
        "embed-and-search",                                     # step ID shown in Inngest dashboard
        lambda: _search(question, top_k),                      # the function to execute inside this step
        output_type=RAGSearchResult                             # tell Inngest the return type so it can deserialize correctly
    )

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)  # format each retrieved chunk as a bullet, joined by blank lines
# simple prompt
    user_content = (
        "Use the following context to answer the question.\n\n"     # instruction to the LLM
        f"Context:\n{context_block}\n\n"                            # inject the retrieved PDF chunks as context
        f"Question: {question}\n"                                   # inject the user's question
        "Answer concisely using the context above."                 # tell the LLM to stay grounded in the context
    )

    adapter = ai.gemini.Adapter(                                # create a Gemini adapter so Inngest knows how to call the API
        api_key=os.getenv("GEMINI_API_KEY"),                    # load the Gemini API key from the .env file
        model="gemini-1.5-flash"                                # the specific Gemini model to use (fast and cost-efficient)
    )
## wer passing to the inference step with our messages
    res = await ctx.step.ai.infer(                              # call the LLM as a tracked Inngest step (retryable, logged)
        "llm-answer",                                           # step ID shown in Inngest dashboard
        adapter=adapter,                                        # which LLM provider/model to use
        body={
            "max_tokens": 768,                                  # maximum number of tokens the LLM can generate in its response
            "temperature": 0.2,                                 # low temperature = more focused/deterministic answers
            "messages": [
                {
                    "role": "system",                           # system message sets the LLM's behaviour/persona
                    "content": "You answer questions using only the provided context."
                },
                {
                    "role": "user",                             # user message contains the actual question + context
                    "content": user_content
                }
            ]
        }
    )
#^parsing the response and returning
    answer = res["choices"][0]["message"]["content"].strip()    # extract the LLM's answer text from the response object

    return {
        "answer": answer,                                       # the LLM's answer to the question
        "sources": found.sources,                               # which PDF sources the answer was based on
        "num_contexts": len(found.contexts)                     # how many chunks were retrieved and used as context
    }



app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf])
