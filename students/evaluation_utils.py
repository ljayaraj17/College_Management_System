import random
import os
import json
from openai import OpenAI

# Initialize OpenAI client
# It will automatically use OPENAI_API_KEY from environment variables

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key="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")
def get_ai_generated_questions(subject_name, semester, course_name):
    """
    Generate 10 MCQ questions using OpenAI based on subject, semester and course.
    """
    prompt = f"""
    Generate 10 high-quality Multiple Choice Questions (MCQs) for a college student.
    
    Context:
    Subject: {subject_name}
    Semester: {semester}
    Course: {course_name}
    
    Requirements:
    - Return exactly 10 questions.
    - Each question should have exactly 4 options.
    - Provide a clear 'explanation' for the correct answer.
    - The output MUST be a valid JSON array of objects.
    - Each object must have these keys: 'question', 'options', 'correct', 'explanation'.
    - The 'options' key should be an array of strings.
    - The 'correct' key should be the exact string matching one of the options.
    
    Return ONLY the JSON.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using mini for cost/speed efficiency
            messages=[
                {"role": "system", "content": "You are an expert academic examiner specialized in generating high-quality test questions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Openai 2.24.0 usually returns json if requested
        data = json.loads(response.choices[0].message.content)
        
        # Handle different potential JSON structures (sometimes AI wraps it in a key)
        if isinstance(data, dict):
            # Try to find the list in common keys like 'questions' or 'mcqs'
            for key in ['questions', 'mcqs', 'results', 'data']:
                if key in data and isinstance(data[key], list):
                    return data[key][:10]
            # If it's a single array in the dict, or just the dict itself (shouldn't be)
            return list(data.values())[0][:10] if data.values() else []
        
        return data[:10]
        
    except Exception as e:
        print(f"AI Generation Error: {e}")
        # Fallback to hardcoded pool if AI fails
        return get_fallback_questions(subject_name)

def get_fallback_questions(subject_name):
    """Pool of questions to use if AI fails"""
    question_pool = {
        "Computer Science": [
            {"id": 1, "question": "Which data structure uses the LIFO principle?", "options": ["Queue", "Stack", "Linked List", "Tree"], "correct": "Stack", "explanation": "A Stack follows LIFO (Last-In-First-Out)."},
            {"id": 2, "question": "What is the time complexity of searching in a Balanced BST?", "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"], "correct": "O(log n)", "explanation": "Logarithmic time is characteristic of balanced search trees."},
            {"id": 3, "question": "In Python, which keyword is used to define a function?", "options": ["func", "define", "def", "function"], "correct": "def", "explanation": "'def' is the standard keyword for function definition in Python."},
            {"id": 4, "question": "Which layer of the OSI model is responsible for routing?", "options": ["Physical", "Data Link", "Network", "Transport"], "correct": "Network", "explanation": "The Network layer (Layer 3) handles routing and IP addressing."},
            {"id": 5, "question": "What does SQL stand for?", "options": ["Simple Query Language", "Structured Query Language", "Standard Query Level", "System Query Logic"], "correct": "Structured Query Language", "explanation": "SQL is the standard language for relational database management."},
            {"id": 6, "question": "Which sorting algorithm has a worst-case complexity of O(n^2)?", "options": ["Merge Sort", "Quick Sort", "Bubble Sort", "Heap Sort"], "correct": "Bubble Sort", "explanation": "Bubble Sort is inefficient with O(n^2) worst-case performance."},
            {"id": 7, "question": "What is the primary purpose of a 'foreign key' in a database?", "options": ["Unique identification", "Establishing relationships", "Speeding up queries", "Data encryption"], "correct": "Establishing relationships", "explanation": "Foreign keys link records between two tables."},
            {"id": 8, "question": "Which of these is NOT a pillar of Object-Oriented Programming?", "options": ["Inheritance", "Encapsulation", "Compilation", "Polymorphism"], "correct": "Compilation", "explanation": "The 4 pillars are Abstraction, Encapsulation, Inheritance, and Polymorphism."},
            {"id": 9, "question": "What is the size of an 'int' in Java (usually)?", "options": ["16 bits", "32 bits", "64 bits", "8 bits"], "correct": "32 bits", "explanation": "Java ints are standard 32-bit signed integers."},
            {"id": 10, "question": "What does CSS stand for in web development?", "options": ["Cascading Style Sheets", "Computer Style Syntax", "Creative Sheet Styles", "Colorful Style System"], "correct": "Cascading Style Sheets", "explanation": "CSS defines the presentation of HTML documents."}
        ],
        "Mathematics": [
            {"id": 11, "question": "What is the derivative of sin(x)?", "options": ["cos(x)", "-cos(x)", "tan(x)", "sec(x)"], "correct": "cos(x)", "explanation": "d/dx[sin(x)] = cos(x)."},
            {"id": 12, "question": "What is the value of Pi (to 2 decimal places)?", "options": ["3.12", "3.14", "3.16", "3.18"], "correct": "3.14", "explanation": "Pi is roughly 3.14159..."},
            {"id": 13, "question": "What is the integral of 1/x dx?", "options": ["x^2", "ln|x|", "e^x", "log(x)"], "correct": "ln|x|", "explanation": "The integral of reciprocal x is the natural logarithm."},
            {"id": 14, "question": "What is the sum of angles in a triangle?", "options": ["90 deg", "180 deg", "270 deg", "360 deg"], "correct": "180 deg", "explanation": "Euclidean triangle angles always sum to 180 degrees."},
            {"id": 15, "question": "What is 2^10?", "options": ["512", "1024", "2048", "1000"], "correct": "1024", "explanation": "2^10 is a common power of 2 used in computing."},
            {"id": 16, "question": "What is the square root of 225?", "options": ["13", "14", "15", "16"], "correct": "15", "explanation": "15 * 15 = 225."},
            {"id": 17, "question": "Solve for x: 2x + 5 = 15", "options": ["5", "10", "7.5", "20"], "correct": "5", "explanation": "2x = 10, so x = 5."},
            {"id": 18, "question": "What is the base of natural logarithms?", "options": ["10", "2", "e", "pi"], "correct": "e", "explanation": "'e' is Euler's number (~2.718)."},
            {"id": 19, "question": "In a right-angled triangle, what is the hypotenuse if sides are 3 and 4?", "options": ["5", "6", "7", "25"], "correct": "5", "explanation": "Pythagorean theorem: 3^2 + 4^2 = 5^2 (9+16=25)."},
            {"id": 20, "question": "What is log10(100)?", "options": ["1", "2", "10", "0"], "correct": "2", "explanation": "10 squared is 100."}
        ],
        "General": [
             {"id": 101, "question": "What is the primary goal of Agile?", "options": ["Documentation", "Iterative development", "Fixed cost", "Fast coding"], "correct": "Iterative development", "explanation": "Agile promotes iterative delivery and feedback."},
             {"id": 102, "question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"], "correct": "Paris", "explanation": "Paris is the capital of France."},
             {"id": 103, "question": "Which planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "correct": "Mars", "explanation": "Mars has a reddish appearance due to iron oxide."},
             {"id": 104, "question": "Who developed the theory of relativity?", "options": ["Newton", "Einstein", "Galileo", "Hawking"], "correct": "Einstein", "explanation": "Albert Einstein developed General and Special Relativity."},
             {"id": 105, "question": "What is the chemical symbol for Gold?", "options": ["Gd", "Ag", "Au", "Fe"], "correct": "Au", "explanation": "Au comes from the Latin word 'Aurum'."},
             {"id": 106, "question": "How many continents are there?", "options": ["5", "6", "7", "8"], "correct": "7", "explanation": "There are 7 continents: Asia, Africa, NA, SA, Antarctica, Europe, Australia."},
             {"id": 107, "question": "Which of these is a primary color?", "options": ["Green", "Purple", "Blue", "Orange"], "correct": "Blue", "explanation": "The primary colors are Red, Blue, and Yellow."},
             {"id": 108, "question": "What is the largest ocean on Earth?", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "correct": "Pacific", "explanation": "The Pacific Ocean is the largest and deepest."},
             {"id": 109, "question": "Who wrote 'Romeo and Juliet'?", "options": ["Dickens", "Shakespeare", "Hemingway", "Austen"], "correct": "Shakespeare", "explanation": "William Shakespeare wrote the famous tragedy."},
             {"id": 110, "question": "What is the boiling point of water (Celsius)?", "options": ["90", "100", "110", "120"], "correct": "100", "explanation": "Water boils at 100 degrees Celsius at sea level."}
        ]
    }
    questions = question_pool.get(subject_name, question_pool["General"])
    return random.sample(questions, min(len(questions), 10))

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

