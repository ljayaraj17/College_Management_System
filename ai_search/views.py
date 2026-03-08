import json
import os
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
try:
    from openai import OpenAI
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    client = None

class PDFChatAssistantView(View):
    def post(self, request):
        # Determine if it's an upload, reset, or a chat request
        if 'pdf_file' in request.FILES:
            return self.handle_upload(request)
        
        try:
            data = json.loads(request.body)
            if data.get('action') == 'reset':
                request.session['pdf_context'] = ''
                request.session['pdf_filename'] = ''
                return JsonResponse({'status': 'success', 'message': 'Context cleared.'})
        except:
            pass

        return self.handle_chat(request)

    def handle_upload(self, request):
        try:
            pdf_file = request.FILES['pdf_file']
            
            # Read PDF content
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            if not full_text.strip():
                return JsonResponse({'status': 'error', 'message': 'Could not extract text from the PDF. It might be empty or image-based.'}, status=400)
            
            # Store in session (limited size, but usually okay for moderate PDFs)
            # For very large PDFs, one should use a database or vector store.
            # Truncate to avoid session size limits if necessary (OpenAI also has token limits)
            request.session['pdf_context'] = full_text[:50000] # Safe limit for session and context
            request.session['pdf_filename'] = pdf_file.name
            
            return JsonResponse({
                'status': 'success', 
                'message': f'PDF "{pdf_file.name}" uploaded and processed successfully!',
                'filename': pdf_file.name
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def handle_chat(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            pdf_context = request.session.get('pdf_context', '')
            pdf_filename = request.session.get('pdf_filename', '')
            
            if pdf_context:
                system_prompt = f"""
                You are a professional AI Assistant specialized in analyzing documents.
                A document named "{pdf_filename}" has been uploaded.
                
                Instructions:
                1. Primarily use the extracted text below to answer questions.
                2. Be professional, concise, and helpful.
                3. If the answer is not in the document but is a general professional or academic question, you may provide a general answer but mention it's not from the document.
                4. If the info IS in the document, definitely use it.
                
                Document Content:
                {pdf_context}
                """
            else:
                system_prompt = """
                You are a professional AI Assistant for the EduPulse College Management System.
                Your goal is to assist students, faculty, and staff with their professional and academic queries.
                
                Instructions:
                1. Maintain a highly professional, helpful, and concise tone.
                2. If the user wants to analyze a specific document, remind them they can upload a PDF using the attachment icon.
                """
                
                # Role-specific context injection
                user = request.user
                if hasattr(user, 'is_faculty') and user.is_faculty:
                    from academics.models import AcademicAdvisor
                    from students.models import StudentProfile
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    
                    # Fetch mentee data similar to DashboardView
                    assignments = AcademicAdvisor.objects.filter(faculty=user, is_active=True)
                    mentees_list = []
                    
                    if assignments.exists():
                        for assignment in assignments:
                            profiles = StudentProfile.objects.filter(
                                course=assignment.course,
                                current_semester=assignment.semester
                            )
                            # Get users with attendance data
                            mentee_users = User.objects.filter(student_profile__in=profiles).select_related('student_profile')
                            for m in mentee_users:
                                mentees_list.append({
                                    'name': m.get_full_name() or m.username,
                                    'id': m.username,
                                    'attendance': float(m.attendance or 0),
                                    'course': m.student_profile.course.code if m.student_profile.course else "N/A",
                                    'semester': m.student_profile.current_semester,
                                    'cgpa': float(m.student_profile.cgpa or 0)
                                })
                    
                    if mentees_list:
                        mentee_data_str = "\n".join([
                            f"- {m['name']} (ID: {m['id']}): Attendance: {m['attendance']}%, Course: {m['course']}, Sem: {m['semester']}, CGPA: {m['cgpa']}"
                            for m in mentees_list
                        ])
                        
                        system_prompt += f"""
                        
                        Faculty Specific Context:
                        You have access to the following students (your mentees):
                        {mentee_data_str}
                        
                        Special Instructions for Faculty:
                        1. You can answer questions about which students are available for volunteering.
                        2. Recommendations for volunteers should generally prioritize students with high attendance (above 85%) and good CGPA.
                        3. If a student has low attendance (below 75%), they should NOT be recommended for volunteering as they need to focus on classes to meet eligibility requirements.
                        4. When asked about volunteering, provide a list of top candidates and explain why you recommended them based on their attendance and academic standing.
                        """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600
            )
            
            ai_message = response.choices[0].message.content
            return JsonResponse({'status': 'success', 'message': ai_message})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
