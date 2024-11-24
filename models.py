from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union


class CollectionCreationRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    configuration: Optional[str] = None
    metadata: Optional[list[str]] = None


class SearchEmbeddingRequest(BaseModel):
    database: str = Field(...)
    embeddings: list[float] = Field(...)
    n: int = 10
    where: Optional[Dict] = None
    where_document: Optional[Dict] = None
    include: list[str] = ["metadatas", "documents", "distances"]


class EmbeddingDictFormat(BaseModel):
    ids: Union[List[str], str]
    embeddings: Union[List[List[float]], list[float]] = None
    metadatas: Union[List[Dict], Dict] = None
    documents: Union[list[str], str] = None


class EmeddingInputFormat(BaseModel):
    database: str = Field(...)
    data_list: Union[List[EmbeddingDictFormat], EmbeddingDictFormat] = Field(...)
