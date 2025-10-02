# qa_generator.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv() 
api_key=os.getenv('GROQ_API_KEY')


# Function to load the context from PDF
def load_pdf_context(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    text = " ".join([page.page_content for page in pages])
    return text[:2000]  # Keep it short for tokens

# Function to build the prompt template
def build_prompt():
    return PromptTemplate(
        input_variables=[
            "context", "exam_level", "total_marks",
            "num_questions", "objective_count", "subjective_count", "history"
        ],
        template=""" 
You are an expert question paper generator, and you must follow all instructions exactly as stated. Do not deviate from the given requirements.

Context:
{context}

History:
{history}

Please generate a **{exam_level}** question paper with exactly **{num_questions} questions**. The question paper must include:
- **Objective questions count**: {objective_count} 
- **Subjective questions count**: {subjective_count}
  - These two counts must be strictly followed. If there is any mismatch in the number of questions, generate the correct amount of each type.
- **Total Marks**: {total_marks}

Ensure that the marks for each question add up to the total marks.
"""
    )

# Function to build the LLMChain
def build_chain():
    prompt = build_prompt()
    llm=ChatGroq(model='gemma2-9b-it',api_key=api_key)
    return LLMChain(llm=llm, prompt=prompt)

def generate_initial_paper(config, pdf_path, history):
    try:
        chain = build_chain()
        context = load_pdf_context(pdf_path)

        if not context.strip():
            print("⚠️ PDF context is empty.")
            return "⚠️ Failed to extract meaningful content from the uploaded PDF."

        inputs = {
            "context": context,
            "exam_level": config["exam_level"],
            "total_marks": config["total_marks"],
            "num_questions": config["num_questions"],
            "objective_count": config["objective_count"],
            "subjective_count": config["subjective_count"],
            "history": "\n".join(history)
        }

        print("🧠 Sending prompt to LLM:")
        print(inputs)

        response = chain.run(inputs)

        if not response.strip():
            print("❌ LLM returned an empty response.")
            return "⚠️ Failed to generate the question paper. Please try again."

        print("📄 Generated Question Paper:")
        print(response)

        history.append(response)  # only append the raw response
        return response

    except Exception as e:
        print("❌ Exception occurred during question generation:", str(e))
        return "⚠️ An error occurred while generating the question paper. Check logs."
