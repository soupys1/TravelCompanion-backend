import chromadb
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def store_result(results):
    store_search = chroma_client.get_or_create_collection(name="store_search")

    ids = []
    documents= [] 
    metadatas= []

    for i, result in enumerate(results["results"]):
        ids.append(str(i))
        documents.append(result["content"])
        metadatas.append({ "url" : result["url"]})
    store_search.add(ids = ids, documents= documents, metadatas= metadatas
                     )

def retrieve_context (query):
    store_retrieve = chroma_client.get_or_create_collection(name="store_search")
    results = store_retrieve.query(

        query_texts= [query],
        n_results= 3
    )
    return results

