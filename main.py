import chromadb
import chromadb.errors
from fastapi import (
    FastAPI,
    HTTPException,
)
import os
from models import (
    CollectionCreationRequest,
    SearchEmbeddingRequest,
    EmeddingInputFormat,
)

PATH = os.environ.get("CHROMA_PATH")
chroma_client = chromadb.PersistentClient(path=PATH)

app = FastAPI()


async def collection_to_dict(collection_response):
    _dict = {
        "id": collection_response.id,
        "name": collection_response.name,
        "configuration_json": collection_response.configuration_json,
        "meta_data": collection_response.metadata,
    }
    return _dict


@app.post("/create_collection")
async def create_collection(collection_data: CollectionCreationRequest):
    try:
        try:
            resp = chroma_client.create_collection(
                name=collection_data.name,
                configuration=collection_data.configuration,
                metadata=collection_data.metadata,
                get_or_create=False,
            )
        except ValueError as e:
            return HTTPException(status_code=422, detail={"errors": e.errors()})

    except ValueError as e:
        return HTTPException(status_code=422, detail={"errors": e.errors()})
    except Exception as e:
        return HTTPException(status_code=500, detail={"error": str(e)})

    response = await collection_to_dict(resp)

    return response


@app.delete("/delete_collection/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        chroma_client.delete_collection(collection_name)
    except ValueError as e:
        return HTTPException(status_code=422, detail={"errors": str(e)})
    except Exception as e:
        return HTTPException(status_code=500, detail={"error": str(e)})


@app.get("/get_collections")
async def get_collections():
    collections = chroma_client.list_collections()
    _list = [
        {
            "id": x.id,
            "name": x.name,
            "configuration_json": x.configuration_json,
            "meta_data": x.metadata,
        }
        for x in collections
    ]
    return _list


@app.post("/search_embbeding")
async def search_embedding(embed_request: SearchEmbeddingRequest):
    try:
        try:
            collections = chroma_client.get_collection(name=embed_request.database)
        except chromadb.errors.InvalidCollectionException as e:
            return HTTPException(
                status_code=422, detail={"error": "collection does not exist"}
            )

        resp = collections.query(
            query_embeddings=embed_request.embeddings,
            include=embed_request.include,
        )
        if (
            "documents" not in resp
            or not resp["documents"]
            or len(resp["documents"][0]) == 0
        ):
            raise ValueError({"detail": "No documents found in query response"})

        docs = [x for x in resp["documents"][0]]
        return docs
    except ValueError as e:
        error_detail = (
            e.args[0] if e.args and isinstance(e.args[0], dict) else {"detail": str(e)}
        )
        return HTTPException(status_code=422, detail=error_detail)
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/add_embedding")
async def add_embbedding(embed_list: EmeddingInputFormat):
    try:
        try:
            collections = chroma_client.get_collection(name=embed_list.database)
        except chromadb.errors.InvalidCollectionException as e:
            return HTTPException(
                status_code=422, detail={"error": "collection does not exist"}
            )
        data_to_add = {
            "ids": embed_list.data_list.ids,
            "metadatas": embed_list.data_list.metadatas,
            "embeddings": embed_list.data_list.embeddings,
            "documents": embed_list.data_list.documents,
        }
        try:
            collections.add(**data_to_add)
        except chromadb.errors.DuplicateIDError as e:
            return HTTPException(status_code=422, detail={"error": e})
        except ValueError as e:
            return HTTPException(status_code=422, detail={"errror": e})
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/create_if_not_exist/{collection_name}")
async def create_if_not_exist(collection_name: str):
    try:
        collection = chroma_client.get_collection(name=collection_name)
        response = await collection_to_dict(collection)
        return response
    except chromadb.errors.InvalidCollectionException:
        collection = chroma_client.create_collection(name=collection_name)
        response = await collection_to_dict(collection)
        return response
    except Exception as e:
        return HTTPException(status_code=422, detail=f"Internal Server Error: {str(e)}")


@app.get("/get_sample/{collection_name}")
async def get_sample(collection_name: str):
    collections = chroma_client.get_collection(name=collection_name)
    resp = collections.peek(limit=10)
    _dict = {
        "ids": resp["ids"],
        "documents": resp["documents"],
        "uris": resp["uris"],
        "data": resp["data"],
        "metadatas": resp["metadatas"],
        "included": resp["included"],
    }
    return _dict
