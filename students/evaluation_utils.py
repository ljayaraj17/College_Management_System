import random

def get_ai_generated_questions(subject_name, semester):
    """
    Simulated AI logic to generate MCQ questions based on subject and semester.
    In a real-world scenario, this would call an LLM API (like GPT-4 or Gemini).
    """
    
    # Pool of high-quality sample questions for demonstration
    question_pool = {
        "Computer Science": [
            {
                "id": 1,
                "question": "Which data structure uses the LIFO (Last-In-First-Out) principle?",
                "options": ["Queue", "Stack", "Linked List", "Tree"],
                "correct": "Stack",
                "explanation": "A Stack follows LIFO, where the last element added is the first one removed."
            },
            {
                "id": 2,
                "question": "What is the time complexity of searching in a Balanced Binary Search Tree?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
                "correct": "O(log n)",
                "explanation": "Balanced trees allow logarithmic search time by halving the search space each step."
            }
        ],
        "Mathematics": [
            {
                "id": 3,
                "question": "What is the derivative of sin(x)?",
                "options": ["cos(x)", "-cos(x)", "tan(x)", "sec(x)"],
                "correct": "cos(x)",
                "explanation": "The basic calculus derivative of the sine function is the cosine function."
            }
        ],
        "General": [
             {
                "id": 101,
                "question": "What is the primary goal of Agile methodology?",
                "options": ["Strict documentation", "Iterative development", "Fixed requirements", "Single phase delivery"],
                "correct": "Iterative development",
                "explanation": "Agile focuses on continuous improvement and iterative cycles."
            }
        ]
    }
    
    # Try to find specific questions, otherwise use General
    questions = question_pool.get(subject_name, question_pool["General"])
    
    # If using a real AI, we would prompt it here:
    # prompt = f"Generate 5 MCQ questions for {subject_name} (Semester {semester}) with explanations."
    
    # Return 5 randomized questions (for now just returning the pool)
    return random.sample(questions, min(len(questions), 5))

def generate_ai_feedback(score, subject_name):
    """Generates feedback based on score"""
    if score >= 80:
        return f"Excellent proficiency in {subject_name}! You have a strong grasp of core concepts."
    elif score >= 50:
        return f"Good effort. You have a foundational understanding of {subject_name}, but some advanced areas need review."
    else:
        return f"It seems you are struggling with some fundamental concepts in {subject_name}. Regular practice is recommended."

def generate_ai_recommendations(score, subject_name):
    """Generates specific learning recommendations"""
    if score >= 80:
        return "1. Explore advanced research papers.\n2. Try implementing complex projects.\n3. Assist peers to reinforce knowledge."
    elif score >= 50:
        return "1. Review textbook chapters on missed questions.\n2. Watch visual tutorials for complex algorithms.\n3. Take more practice quizzes."
    else:
        return "1. Start from basics (Tutorials/Intro books).\n2. Consult with your Faculty Mentor.\n3. Join a study group for peer support."
