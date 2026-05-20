import pydantic
## create some custom Python types
# i cana make my  app a little bit  more readable a
class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]
    source_id: str = None

class RAGUpsertResult(pydantic.BaseModel):
    ingested: int

class RAGSearchResult(pydantic.BaseModel):
    contexts: list[str]
    sources: list[str]


## this different than the search result.this is the query that the user is actually sending
## to the endppoint . pydantic.BaseModel
class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int



