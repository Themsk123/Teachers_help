# feedback_handler.py
from utils.qa_generator import generate_initial_paper

def give_feedback(feedback, config, pdf_path, history):
    # Step 1: Store feedback in history
    history.append(f"Feedback: {feedback}")
    
    print("\n📝 Generating Updated Paper based on feedback...")

    # Step 2: Call the QA generator to regenerate the paper based on feedback
    # You can modify the config or prompt structure based on feedback here.
    generate_initial_paper(config, pdf_path, history)

    # Step 3: Optionally, you can tweak this logic based on feedback to alter the paper generation logic
    # For example, modifying config or prompt structure dynamically.
