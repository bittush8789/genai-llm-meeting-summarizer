import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()


def get_llm(model_name: str = "llama-3.3-70b-versatile"):
    """Initialize and return the Groq Chat model."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY environment variable is not set. Please update the .env file.")
        
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=0.2
    )


def generate_meeting_summary(transcript: str, model_name: str = "llama-3.3-70b-versatile") -> str:
    """Generates an executive summary of the meeting transcript."""
    llm = get_llm(model_name)
    
    template = """You are a highly efficient meeting secretary. 
Your task is to write a clean, clear, and comprehensive executive summary of the following meeting transcript.
Highlight the primary topics of discussion, the main talking points, and the overall outcome of the meeting. Keep the language professional.

Transcript:
{transcript}

Executive Summary:"""

    prompt = PromptTemplate(template=template, input_variables=["transcript"])
    chain = prompt | llm
    
    response = chain.invoke({"transcript": transcript})
    return response.content.strip()


def extract_action_items(transcript: str, model_name: str = "llama-3.3-70b-versatile") -> list:
    """Extracts action items from the meeting transcript and returns them as a list of strings."""
    llm = get_llm(model_name)
    
    template = """You are a highly efficient meeting secretary.
Your task is to identify and extract all actionable tasks, action items, and next steps from the following meeting transcript.
List each action item on a new line starting with a dash (-). If a specific person is assigned to the task, write their name in parentheses next to the task, e.g., "Review Q3 marketing plan (Alice)". If no assignee is mentioned, list the item without parentheses.
Do not write any introductory or concluding text, only return the list of action items. If there are no action items, output nothing.

Transcript:
{transcript}

Action Items:"""

    prompt = PromptTemplate(template=template, input_variables=["transcript"])
    chain = prompt | llm
    
    response = chain.invoke({"transcript": transcript})
    
    # Process string response into a clean Python list
    action_items = []
    for line in response.content.split("\n"):
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            # Remove bullet point and whitespace
            item = line[1:].strip()
            if item:
                action_items.append(item)
        elif line:
            # Fallback if no bullet points but there is text
            action_items.append(line)
            
    return action_items


def extract_decisions(transcript: str, model_name: str = "llama-3.3-70b-versatile") -> str:
    """Extracts key decisions made during the meeting."""
    llm = get_llm(model_name)
    
    template = """You are a highly efficient meeting secretary.
Your task is to identify and extract all key decisions, agreements, resolutions, and conclusions reached in the following meeting transcript.
List them clearly.
Do not write any introductory or concluding text, only return the findings. If no decisions were made, write "No major decisions were explicitly recorded."

Transcript:
{transcript}

Decisions:"""

    prompt = PromptTemplate(template=template, input_variables=["transcript"])
    chain = prompt | llm
    
    response = chain.invoke({"transcript": transcript})
    return response.content.strip()
