from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from .forms import UploadFileForm
from .models import UploadedFile
from .models import Note
from utils.note_maker import run_note_maker  # Your existing script
from utils.feedback_handler import give_feedback  # Your existing script
from utils.pdf_generator import generate_pdf_response

def home_view(request):
    return render(request, 'accounts/home.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_path = uploaded_file.file.path  # Absolute path to the file
            return render(request, 'accounts/upload_success.html', {'file_path': file_path})
    else:
        form = UploadFileForm()
    return render(request, 'accounts/upload.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Get the 'next' parameter from GET or POST
    next_url = request.GET.get('next', request.POST.get('next', 'home'))

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')
    return redirect('home')


@login_required
def upload_video(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        num_pages = 3  # or get from form
        try:
            results = run_note_maker(youtube_url, num_pages, "teacher_session", [])
            # Save the generated notes
            note = Note.objects.create(
                user=request.user,
                youtube_url=youtube_url,
                content=results[0][1]  # Store the initial summary/content
            )
            # Redirect to the notes page with the note's ID
            return redirect('view_notes', note_id=note.id)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('upload_video')
    return render(request, 'accounts/upload.html')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note
from utils.pdf_generator import generate_pdf_response  # Make sure this import path is correct
from utils.feedback_handler import give_feedback  # Adjust this if your feedback function is in a different file

@login_required
def view_notes(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        if feedback:
            try:
                # Process feedback with chatbot
                updated_results = give_feedback(feedback, {}, note.youtube_url, [note.content])
                note.content = updated_results[-1][1]  # Safely get the updated note
                note.save()
            except Exception as e:
                return render(request, 'accounts/notes.html', {
                    'note': note,
                    'error': f"Failed to update notes with feedback: {e}"
                })

    # Optional PDF download trigger
    if 'download_pdf' in request.GET:
        return generate_pdf_response(note.content, filename=f"note_{note_id}.pdf")

    return render(request, 'accounts/notes.html', {'note': note})



# accounts/views.py

from django.http import HttpResponseBadRequest
from pypdf.errors import PdfStreamError
from .models import Note
from utils.pdf_generator import generate_pdf_response  # Your PDF generation function

@login_required
def generate_pdf(request, note_id):
    try:
        note = Note.objects.get(id=note_id)
        return generate_pdf_response(note.content)
    except PdfStreamError as e:
        return HttpResponseBadRequest(f"PDF generation failed: {str(e)}")
    except Note.DoesNotExist:
        return HttpResponseBadRequest("Note does not exist.")
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
    

from django.http import HttpRequest, HttpResponse
from typing import Any
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import tempfile

from utils.qa_generator import generate_initial_paper
from utils.feedback_handler import give_feedback
from utils.pdf_generator import generate_pdf_response
from .forms import QnAUploadForm

# ---- Helper Functions ----

def handle_uploaded_file(file) -> str:
    """Saves uploaded file temporarily and returns the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        return temp_file.name

def calculate_question_counts(num_questions: int, qtype: str) -> tuple[int, int]:
    """Returns objective and subjective question counts based on type."""
    if qtype == "objective":
        return num_questions, 0
    elif qtype == "subjective":
        return 0, num_questions
    else:  # both
        obj = num_questions // 2
        sub = num_questions - obj
        return obj, sub

# ---- View: Upload Notes and Generate QnA ----

@login_required
def upload_qna(request: Any) -> HttpResponse:
    if request.method == 'POST':
        form = QnAUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Step 1: Collect input
            config = {
                "exam_level": form.cleaned_data['exam_level'],
                "num_questions": form.cleaned_data['num_questions'],
                "total_marks": form.cleaned_data['total_marks'],
            }
            config["objective_count"], config["subjective_count"] = calculate_question_counts(
                config["num_questions"], form.cleaned_data['question_type']
            )

            # Step 2: Save the uploaded file temporarily
            temp_path = handle_uploaded_file(request.FILES['file'])

            # Step 3: Generate the initial question paper
            history = []
            generated = generate_initial_paper(config, temp_path, history)
            print("✅ Generated QnA Output:")
            print(generated)

            # Step 4: Store all in session
            request.session['qna'] = generated
            request.session['qna_config'] = config
            request.session['qna_history'] = history
            request.session['qna_file_path'] = temp_path

            return redirect('view_qna')
    else:
        form = QnAUploadForm()

    return render(request, 'accounts/upload.html', {'form': form})

# ---- View: View / Update / Download QnA ----

@login_required
def view_qna(request: Any) -> HttpResponse:
    qna = request.session.get('qna', '')
    history = request.session.get('qna_history', [])
    temp_path = request.session.get('qna_file_path')
    config = request.session.get('qna_config')

    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        if feedback:
            give_feedback(feedback, config, temp_path, history)
            updated_qna = history[-1] if history else qna
            request.session['qna'] = updated_qna
            request.session['qna_history'] = history
            qna = updated_qna

    if 'download_pdf' in request.GET:
        return generate_pdf_response(qna, filename="qna_output.pdf")

    return render(request, 'accounts/view_qna.html', {'qna': qna})
