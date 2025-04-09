
from fastapi import FastAPI, Form, Request, Response, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.responses import FileResponse
import os
import aiofiles
import csv
from datetime import datetime
import uvicorn
# Initialize FastAPI app
app = FastAPI()

# Mount the static directory to serve files (for storing PDFs and outputs)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set OpenAI API Key (Make sure to replace with your actual key)
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_KEY")


# Function to process uploaded PDF

def process_pdf(file_path):
    """
    Extracts text from a PDF, splits it into chunks, and returns structured documents.
    """
    loader = PyPDFLoader(file_path)
    data = loader.load()  # Load text from the PDF

    # Combine all pages into a single string
    pdf_text = "".join([page.page_content for page in data])

    # Split text into large chunks for question generation
    splitter_ques_gen = TokenTextSplitter(chunk_size=10000, chunk_overlap=200)
    question_chunks = splitter_ques_gen.split_text(pdf_text)

    # Split text into smaller chunks for answer generation
    splitter_ans_gen = TokenTextSplitter(chunk_size=1000, chunk_overlap=100)
    answer_chunks = splitter_ans_gen.split_text(pdf_text)

    return question_chunks, answer_chunks


# Function to generate questions and store embeddings

def generate_questions(file_path):
    """
    Generates questions from the extracted text and stores embeddings in FAISS.
    """
    question_chunks, answer_chunks = process_pdf(file_path)

    # Initialize OpenAI LLM for question generation
    # llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    # Define prompt template for generating questions
    prompt_template = PromptTemplate(
        template="""
        You are an expert at creating questions based on the text below:
        ------------
        {text}
        ------------
        Generate a list of 10 most relevant questions.
        """,
        input_variables=["text"]
    )

    # Generate questions using LLM
    questions = [llm.predict(prompt_template.format(text=chunk)) for chunk in question_chunks]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(answer_chunks, embeddings)
    retriever = vector_store.as_retriever()

    # Create an LLM-based QA system
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return questions, qa_chain


# Function to generate answers and save to CSV

def save_qa_to_csv(file_path):
    """
    Generates answers for the generated questions and saves them in a CSV file.
    """
    questions, qa_chain = generate_questions(file_path)
    output_file = "static/output/QA.csv"

    # Ensure the output directory exists
    os.makedirs("static/output", exist_ok=True)

    # Write the questions and answers to a CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Question", "Answer"])

        for question in questions:
            answer = qa_chain.run(question)
            csv_writer.writerow([question, answer])

    return output_file


# API route for uploading PDF
@app.post("/upload")
async def upload_pdf(pdf_file: bytes = File(...), filename: str = Form(...)):
    """
    Uploads the PDF and saves it to the static/docs/ directory.
    """
    base_folder = "static/docs/"
    os.makedirs(base_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Split original filename to insert timestamp before extension
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    # Join with the base folder
    pdf_filepath = os.path.join(base_folder, new_filename)
    # pdf_filepath = os.path.join(base_folder, filename)

    # Save file asynchronously
    async with aiofiles.open(pdf_filepath, 'wb') as f:
        await f.write(pdf_file)

    output_file = save_qa_to_csv(pdf_filepath)
    return FileResponse(
        path=output_file,
        filename="QA.csv",
        media_type="text/csv"
    )


# data=save_qa_to_csv("static/Code of Conduct (1).pdf")
# print(data)