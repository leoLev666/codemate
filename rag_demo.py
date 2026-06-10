import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 加载 .env 中的 API Key
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    print("错误：未找到 DEEPSEEK_API_KEY，请在 .env 文件中设置或设置环境变量")
    sys.exit(1)

loader = TextLoader("sample.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(docs, embedding_model, persist_directory="./chroma_db")
vectorstore.persist()

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1",
)
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

answer = qa_chain.invoke("2025年智能家居市场规模是多少？")
print(answer)