import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Path to store vector database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vectorstore")


def store_transcript_in_chroma(meeting_id: int, title: str, transcript: str):
    """
    Splits the transcript into paragraphs/chunks, generates embeddings 
    using sentence-transformers ('all-MiniLM-L6-v2'), and stores them in ChromaDB.
    """
    try:
        # Initialize persistent client
        client = chromadb.PersistentClient(path=DB_PATH)
        
        # Use sentence-transformers embedding function
        embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name="meeting_transcripts",
            embedding_function=embedding_function
        )
        
        # Simple splitting by paragraph/sentences
        chunks = [c.strip() for c in transcript.split("\n\n") if c.strip()]
        if not chunks:
            # If no double newlines, try single newlines
            chunks = [c.strip() for c in transcript.split("\n") if c.strip()]
        if not chunks:
            # Fallback to entire transcript as a single chunk
            chunks = [transcript]

        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            ids.append(f"meeting_{meeting_id}_chunk_{i}")
            documents.append(chunk)
            metadatas.append({
                "meeting_id": meeting_id,
                "title": title,
                "chunk_index": i
            })
            
        if documents:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Stored {len(documents)} chunks in ChromaDB for meeting ID {meeting_id}")
    except Exception as e:
        print(f"Error saving to ChromaDB: {e}")
        # We don't want to crash the entire application if ChromaDB has an issue
        raise e
