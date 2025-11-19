from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import faiss


import getpass
import os

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=100,
)


embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
embedding_dim = len(embeddings.embed_query("hello"))

index = faiss.IndexFlatL2(embedding_dim)
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

# Chat memory
memory = []


def get_response(user_message, retrieved_docs):
    print("Getting response please wait...")
    results_text = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder("history"),
        ("system", "Relevant documents:\n{results}"),
        ("human", "{input}")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "input": user_message,
        "history": memory,
        "results": results_text
    })

    # Save chat history
    memory.append(HumanMessage(content=user_message))
    memory.append(AIMessage(content=response.content))

    if len(memory) > 3:
        del memory[:-3]

    return response.content

    
user_message="what is the process of getting car loan?"

# Retrieve relevant context
results = vector_store.similarity_search(user_message, k=2)
reply = get_response(user_message, results)
print(reply)




