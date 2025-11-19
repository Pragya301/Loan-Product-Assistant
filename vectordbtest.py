import getpass
import os

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
import faiss

# Load file
loader = TextLoader(r"C:\Users\pragy\OneDrive\Desktop\pyproject\scraped_data")
documents = loader.load()

# Semantic chunking
semantic_chunker = SemanticChunker(embeddings)
docs = semantic_chunker.split_documents(documents)     

# Create empty FAISS index
embedding_dim = len(embeddings.embed_query("hello")) 
index = faiss.IndexFlatL2(embedding_dim)

# Create vectorstore
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

# Add chunks one-by-one
for doc in docs:
    uid = str(uuid4())
    vector_store.add_documents(documents=[doc], ids=[uid])
