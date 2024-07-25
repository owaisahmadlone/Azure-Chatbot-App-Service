import pyodbc
import json
import ssl
import urllib.request
import os
import random
import string
from pymilvus import MilvusClient,Collection,connections
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import Answer


embedding_model = HuggingFaceEmbeddings()
milvus_collection_name = "Chunk_Vector_Index"


# Mistral API details
MISTRAL_URL = ''
MISTRAL_API_KEY = ''

# SQL Server connection details
SQL_SERVER = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''
DRIVER = '{ODBC Driver 17 for SQL Server}'

SQL_CONN_STRING= f'DRIVER={DRIVER};SERVER=tcp:{SQL_SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

# Milvus connection details
MILVUS_URI = "http://4.213.193.212:19530"

def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def get_system_prompt_with_pdf(last_question, last_answer, context):
    if last_question == "":
        return f"""
        Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
        Use the following pieces of information enclosed in <context> tags as well your unmatched understanding of things to provide an answer to the questions asked. You always think
        step by step.
        <context>
        {context}
        </context>
        """
    else:
        return f"""
        Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
        Use the following pieces of information enclosed in <context> tags as well your unmatched understanding of things to provide an answer to the questions asked. You always think
        step by step.
        <context>
        Question:
        {last_question}

        Answer:
        {last_answer}

        Information:
        {context}
        </context>
        """

def get_system_prompt_without_pdf(last_question,last_answer):
    if last_question == "":
        return f"""
        Human: You are an AI assistant. You are able to answer question from a wide range of fields due to your
        unmatched knowledge of vastly all topics or fields. Your answers are always relevant to the question asked and
        you are very careful about not providing wrong or deceitful information. think step by step while answering the question.
        """
    else:
        return f"""
        Human: You are an AI assistant. You are able to answer question from a wide range of fields due to your
        unmatched knowledge of vastly all topics or fields. Your answers are always relevant to the question asked and
        you are very careful about not providing wrong or deceitful information.
        Use the following examples of questions and their answers enclosed in <context> tags as well your unmatched understanding of things to provide an answer to the questions asked.
        <context>
        {last_question}
        {last_answer}
        Let's think step by step
        </context>
        """


def get_mistral_input(question,system_prompt):
    return {
        "messages": [
            {
                "role": "user",
                "content": f"{question}"
            },
            {
                "role": "assistant",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"{question}"
            }
        ],
        "max_tokens": 8192,
        "temperature": 0.4,
        "top_p": 1,
        "safe_prompt": "false"
    }

def connect_to_sql():
    # Connect to a SQL database
    conn = pyodbc.connect(SQL_CONN_STRING)
    return conn.cursor()

def connect_to_milvus():
    # Connect to Milvus database
    milvus_client = MilvusClient(uri=MILVUS_URI)
    return milvus_client

def parse_pdf(file_location):
    # Parse the text from a PDF file
    loader = PyPDFLoader(file_location)
    documents = loader.load()
    return documents

def chunk_text(documents):
    # Chunk the text into smaller pieces
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    return chunks

def embed_text(text):
    # Embed the text using a pre-trained model
    return embedding_model.embed_query(text)

async def upload_to_vector_db(chunks,file_name:str):
    milvus_client = connect_to_milvus()

    if milvus_client.has_collection(collection_name=milvus_collection_name) is False:
        milvus_client.create_collection(
            collection_name=milvus_collection_name,
            dimension=len(embedding_model.embed_query('Test query')),
            metric_type="COSINE",  # COSINE similarity
            consistency_level="Strong",  # Strong consistency level
        )
    
    # global partition_name
    # NOTE: inserting the chunks into the default partition for now
    
    # If creating a seperate partition for the file
    # partition_name = f"partition_{file_name.split('.pdf')[0]}_{''.join(random.choices(string.digits+string.ascii_letters,k=10))}"
    # Create a partition
    # milvus_client.create_partition(collection_name=milvus_collection_name,partition_name=partition_name,description=f"Vector Index for {file_name}")
    
    # Upload the text chunks to a vector database
    res = milvus_client.query(collection_name=milvus_collection_name, output_fields=["count(*)"])
    num_rows = res[0]["count(*)"]
    data = []
    for i, chunk in enumerate(chunks):
        data.append({"id": num_rows+i, "vector": embed_text(chunk.page_content), "text": chunk.page_content,'source':chunk.metadata['source'],'page':chunk.metadata['page']})
    collection_name = milvus_collection_name
    milvus_client.insert(collection_name=collection_name, data=data)
    print("Uploaded to Vector DB successfully!!")
    

async def generate_model_response(question, conversation_history,pdf_uploaded:bool):
    # byepass server side certificate verification
    allowSelfSignedHttps(True)
    
    # Generate a response using a model
    milvus_client = connect_to_milvus()

    SYSTEM_PROMPT=""

    # If pdf uploaded retrieve relevant chunks from the pdf else generate answer from LLM knowledge
    if pdf_uploaded:
        search_res = milvus_client.search(
            collection_name=milvus_collection_name,
            data=[
                embed_text(question)
            ],  # Use the `embed_text` function to convert the question to an embedding vector
            limit=3,  # Return top 3 results
            search_params={"metric_type": "COSINE", "params": {}},  # Cosine Similarity
            output_fields=["text","source","page"],  # Return the text field
        )
        retrieved_chunks = [res["entity"]["text"] for res in search_res[0]]
        retreived_sources = [res["entity"]["source"] for res in search_res[0]]
        retreived_pages = [res["entity"]["page"] for res in search_res[0]]
        context = "\n".join([chunk for chunk in retrieved_chunks])
        last_question = conversation_history[-2] if conversation_history else ""
        last_answer = conversation_history[-1] if conversation_history else ""
        SYSTEM_PROMPT = get_system_prompt_with_pdf(last_question, last_answer, context)
    else:
        last_question = conversation_history[-2] if conversation_history else ""
        last_answer = conversation_history[-1] if conversation_history else ""
        SYSTEM_PROMPT = get_system_prompt_without_pdf(last_question,last_answer)
    input = get_mistral_input(question, SYSTEM_PROMPT)
    message_body = json.dumps(input).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + MISTRAL_API_KEY)}
    req = urllib.request.Request(MISTRAL_URL, message_body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        result = json.loads(result)
        return Answer(answer = result["choices"][0]["message"]['content'],ref_chunks=retrieved_chunks,ref_docs=retreived_sources,ref_pages=retreived_pages)
    except urllib.error.HTTPError as error:
        return Answer(answer = f"The request failed with status code: {error.code}\n\n{error.info()}\n\n{error.read().decode('utf8', 'ignore')}")
