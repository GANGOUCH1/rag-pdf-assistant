from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct




class QdrantStorage:
    def __init__(self, url="http://localhost:63333", collection="docs", dim=768):
        #### in Porducttion solution we deploy this DB into the AWS
# collection where we stor the in Info
        # with this quadarnt DB it is high performance and we can run it locally
        # however in production u deploy this database out and u probably end up changing this url
        # so u r connecting to the deployed instance or u r using quadrants kind of managed service
        self.client = QdrantClient(url=url , timeout= 30)
        self.collection = collection # we store that as a var
        self.dim = dim
        # create new collectionin our DB
        # create a new collection in our DB inside of this QdrantStorage folder
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vector_config= VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [PointStruct(id=ids[i], vector=vectors[i], payloads=payloads[i]) for i in range(len(ids))]
        self.client.upsert(self.collection, points=points)
# we pass a series of ids which is a list a bunch of vector and which kind of the vectorized verison that's gonna be in a dim=3072
# ## ANDpAYdloads is gonna be real data that's actually human readable they knd of represents the info
### that we've vectorized we gonna convert all these ( ids, vectors, payloads) into this PointStruture
### which is just what's required for it quadrant and the way that we'r doing this, and we'r going to insert
### that into the vector database . SO TAHT ALLOW US TO NOW ADD VECTORS EFFECTIVELLY #
    def search(self, query_vector, top_k=10):

        results = self.client.search(
            collection_name=self.collection,
            query_vector= query_vector,
            with_payload= True,
            limit=top_k
        )
        contexts = []
        sources= set()

        for r in results:
            payload = getattr(r, "payload", None) or { }
            text = payload.get("text", "")
            source = payload.get("source","")
            if text:
                contexts.append(text)
                sources.append(source)
        return {"contexts": contexts, "sources": list(sources)}
# this what goonna do  list(sources search our vector DB it's gonna get the relevant results
### based on this query vector which again we'll look at in a little bit and then we'r gonna
## ppull out all of the sources and the context


### NOTE THAT the way I've done this is that we'r gonna lose which context is associate storyy
## with which source so if we wanna to we cauld cahnge it back and then we would have kind of the related data based on the indices
## in this case it's fine to have it as a set

### NEXT thing that is have a way to read  in a pdf we make a new file data_loader.py
