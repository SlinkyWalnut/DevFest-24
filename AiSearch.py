import os
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import AzureBlobStorageContainerLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

model: str = "text-embedding-ada-002"

print(os.environ.get('AZURE_COGNITIVE_SEARCH_SERVICE_NAME'))

vector_store_address: str = f"https://{os.environ.get('AZURE_COGNITIVE_SEARCH_SERVICE_NAME')}.search.windows.net"

print(vector_store_address)
embeddings: OpenAIEmbeddings = OpenAIEmbeddings(deployment=model, chunk_size=1)
index_name: str = "langchain-vector-demo"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=os.environ.get("AZURE_COGNITIVE_SEARCH_API_KEY"),
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

loader = AzureBlobStorageContainerLoader(
    conn_str=os.environ.get("AZURE_CONN_STRING"),
    container=os.environ.get("CONTAINER_NAME"),
)
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)
vector_store.add_documents(documents=docs)

print("Data loaded into vectorstore successfully")