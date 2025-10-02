from langchain_community.document_loaders import YoutubeLoader
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import re,os
from utils.me import MainText

# STEP 1: Get YouTube Transcript
def get_transcript(video_url):
    ans=MainText(video_url)
    return ans.last_fun()
   

# STEP 2: Create prompt content based on user preferences
def get_prompt_content(transcript, num_pages, user_input=""):
    return f"""
 You are a helpful note-making assistant. Summarize the following YouTube transcript into well-structured, concise notes that fit approximately {num_pages} A4 pages or slides. The content should be educational, formatted with bullet points, subheadings, and concise explanations.

    For each page or slide:
    - Provide a **clear, informative title** for the section (e.g., "Introduction to AI", "Machine Learning Basics").
    - Use **bullet points** to highlight the main points and key takeaways.
    - Include **examples** where applicable, making them short and easy to understand.
    - Break down complex topics with **subheadings** for clarity.
    - Ensure that each section is easy to read, concise, and directly relevant to the transcript.

    The notes should be divided as follows:
    - **Pages/Slides should be formatted** with minimal but effective text that fits neatly into an educational slide or note format.
    - **Avoid long paragraphs**, focus on making the content **digestible** for students or teachers.

    Keep the tone educational and accessible to a wide range of learners.

    **Important:**
    - If the user asks for anything **unrelated** or **irrelevant** to summarizing the transcript or making the notes (e.g., personal requests, off-topic queries), **do not answer**.
    - Strictly focus only on the task at hand: summarizing the YouTube transcript into well-structured, concise notes.
    - If a query is irrelevant, respond with: "This is beyond the scope of the current task. Please provide relevant instructions related to the note-making process."
    

Transcript:
{transcript}
"""

# STEP 3: Memory Setup
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# STEP 4: Setup Model
llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="AIzaSyBsru1X4dcgEomAWMnV6LkJ14d7qcU@vv4")
model_with_memory = RunnableWithMessageHistory(llm, get_session_history)

# STEP 5: Main entry function
def run_note_maker(video_url, num_pages, session_id="firstchat", feedbacks=[]):
    config = {"configurable": {"session_id": session_id}}

    transcript = get_transcript(video_url)
    initial_prompt = get_prompt_content(transcript, num_pages)
    
    # Initial Summary
    response = model_with_memory.invoke([HumanMessage(content=initial_prompt)], config=config)
    results = [("\n--- Initial Summary ---\n", response.content)]

    # Feedbacks
    for msg in feedbacks:
        reply = model_with_memory.invoke([HumanMessage(content=msg)], config=config)
        results.append((f"\n--- Feedback: {msg} ---\n", reply.content))
    
    return results

