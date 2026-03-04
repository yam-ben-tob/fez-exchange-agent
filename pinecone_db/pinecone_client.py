import os
from pinecone import Pinecone
from utils.llmod_client import get_embedding
from utils.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, TOP_K_RESULTS, supabase

def _get_index():
    if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
        raise ValueError("Pinecone credentials missing. Check your .env/config.")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)

def upsert_embeddings(vectors, metadatas=None, namespace=None):
    """
    Upsert a batch of embeddings into Pinecone.
    vectors: list of (id, embedding) tuples or dicts
    metadatas: list of metadata dicts (optional)
    namespace: Pinecone namespace (optional)
    """
    # Pinecone upsert expects list of dicts: {"id": ..., "values": ..., "metadata": ...}
    print(f"Upserting {len(vectors)} embeddings to Pinecone... (namespace: {namespace})")
    index = _get_index()
    items = []
    for i, (id, embedding) in enumerate(vectors):
        if i % 100 == 0:
            print(f"  Preparing item {i+1}/{len(vectors)}: {id}")
        item = {"id": id, "values": embedding}
        if metadatas and i < len(metadatas):
            item["metadata"] = metadatas[i]
        items.append(item)
    print(f"Sending {len(items)} items to Pinecone...")
    index.upsert(vectors=items, namespace=namespace)
    print("Upsert complete.")

# Pinecone DB holds chunks text as metadata for retrieval.
# Still having optio to fetch text from Supabase factsheets_chunks.
def _fetch_chunk_text_by_id(chunk_id: str) -> str:
    """Fetch chunk text from Supabase factsheets_chunks by parsed chunk_id (country_university_filename_index)."""
    if not supabase:
        return ""
    parts = chunk_id.rsplit("_", 1)
    if len(parts) != 2:
        return ""
    prefix, idx_str = parts
    try:
        idx = int(idx_str)
    except ValueError:
        return ""
    # prefix is country_university_filename; file_name contains "."
    subparts = prefix.split("_")
    dot_idx = next((i for i, p in enumerate(subparts) if "." in p), None)
    if dot_idx is None or dot_idx < 1:
        return ""
    country = subparts[0]
    university = "_".join(subparts[1:dot_idx])
    file_name = "_".join(subparts[dot_idx:])
    try:
        r = supabase.table("factsheets_chunks").select("text").eq("country", country).eq("university", university).eq("file_name", file_name).eq("chunk_index", idx).limit(1).execute()
        if r and getattr(r, "data", None) and len(r.data) > 0:
            return r.data[0].get("text", "") or ""
    except Exception:
        pass
    return ""

def query_embedding_text_from_table(query, top_k=TOP_K_RESULTS, namespace=None, filter=None, return_texts=True):
    """
    Query Pinecone for similar embeddings.
    query: string query to embed and search
    top_k: number of results
    namespace: Pinecone namespace (optional)
    filter: metadata filter (optional)
    return_texts: if True, return list of chunk text strings
    """
    index = _get_index()
    query_vector = get_embedding(query)
    response = index.query(vector=query_vector, top_k=top_k, namespace=namespace, filter=filter, include_metadata=True)
    if not return_texts:
        return response
    texts = []
    matches = getattr(response, "matches", []) or response.get("matches", [])
    for m in matches:
        meta = getattr(m, "metadata", None) or (m.get("metadata") if isinstance(m, dict) else {})
        text = meta.get("text", "") if isinstance(meta, dict) else ""
        if not text:
            mid = getattr(m, "id", None) or m.get("id", "")
            if mid and "_" in mid:
                text = _fetch_chunk_text_by_id(str(mid))
        texts.append(text or "")
    return texts

def query_embedding(query, top_k=TOP_K_RESULTS, filter=None):
    index = _get_index()
    query_vector = get_embedding(query)
    response = index.query(
        vector=query_vector, 
        top_k=top_k, 
        filter=filter, 
        include_metadata=True
    )
    
    # Return a dictionary containing BOTH the metadata and the score
    return [
        {
            "id": m.get("id"),
            "metadata": m.get("metadata", {}), 
            "score": m.get("score", 0.0)
        } 
        for m in response.get("matches", [])
    ]

def format_retrieval_context(retrieved_metadata_list):
    """
    Converts list of Pinecone metadata dicts into a structured string.
    Focuses on University, Country, and Section Headers.
    """
    if not retrieved_metadata_list:
        return "No relevant context found."

    context_blocks = []
    
    for meta in retrieved_metadata_list:
        uni = meta.get("university", "Unknown University")
        country = meta.get("country", "Unknown Country")
        content = meta.get("text", "").strip()
        
        headers_dict = meta.get("headers", {})
        h1 = headers_dict.get("Header 1", "")
        h2 = headers_dict.get("Header 2", "")
        h3 = headers_dict.get("Header 3", "")
        
        # Create the Breadcrumb path
        breadcrumb = " > ".join(filter(None, [h1, h2, h3]))
        
        # Construct the Label (University | Country | Section)
        label = f"### UNIVERSITY: {uni} ({country})"
        if breadcrumb:
            label += f" | SECTION: {breadcrumb}"
        
        # Build the final block
        formatted_chunk = f"{label}\n{content}"
        context_blocks.append(formatted_chunk)

    # Clear separator for GPT-5 Mini to distinguish different facts
    return "\n\n---\n\n".join(context_blocks)