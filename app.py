# Import necessary libraries
import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename  # For securing filenames
from PyPDF2 import PdfMerger
from io import BytesIO  # For in-memory file handling
import uuid  # For generating unique identifiers
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for session management
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded files
app.config['MERGED_FOLDER'] = 'merged'  # Directory to store merged files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size limit

# Initialize Flask-Login and Flask-Bcrypt
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "login"

# Dummy user store - replace with your user management logic
users = {
    "test_user": bcrypt.generate_password_hash("password123").decode('utf-8')
}

def get_user(username):
    return users.get(username)

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    Args:
        filename (str): Name of the file to check
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def merge_pdfs(pdf_files):
    """
    Merge multiple PDF files into a single PDF
    Args:
        pdf_files (list): List of paths to PDF files to merge
    Returns:
        BytesIO: In-memory buffer containing the merged PDF
    """
    merger = PdfMerger()
    
    try:
        # Append each PDF file to the merger
        for pdf_path in pdf_files:
            merger.append(pdf_path)
        
        # Write the merged PDF to an in-memory buffer
        output = BytesIO()
        merger.write(output)
        output.seek(0)  # Reset buffer position to start
        return output
    finally:
        # Always close the merger to free resources
        merger.close()

def safe_remove_file(file_path):
    """
    Safely remove a file from the filesystem
    Args:
        file_path (str): Path to the file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        app.logger.error(f"Error removing file {file_path}: {str(e)}")

def get_session_files():
    """
    Get the list of files from the session, initialize if not exists
    Returns:
        list: List of file information dictionaries
    """
    if 'pdf_files' not in session:
        session['pdf_files'] = []
    return session['pdf_files']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Main route for displaying the upload form
    Returns:
        str: Rendered HTML template with file list
    """
    if 'pdf_files' not in session:
        session['pdf_files'] = []
    
    return render_template('index.html', files=session['pdf_files'])

@app.route('/upload', methods=['POST'])
def add_files():
    """
    Handle file upload requests via AJAX
    Returns:
        json: Response with upload status and file information
    """
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files selected'}), 400

    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    uploaded_files = []
    
    try:
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename to prevent conflicts
                original_filename = secure_filename(file.filename)
                filename = f"{str(uuid.uuid4())}_{original_filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Store file information in session
                file_info = {
                    'id': str(uuid.uuid4()),
                    'name': original_filename,
                    'path': file_path
                }
                session['pdf_files'] = get_session_files() + [file_info]
                uploaded_files.append(file_info)
            else:
                return jsonify({'error': 'Only PDF files are allowed'}), 400

        session.modified = True
        return jsonify({
            'message': 'Files uploaded successfully',
            'files': uploaded_files
        })
        
    except Exception as e:
        app.logger.error(f"Error during file upload: {str(e)}")
        # Clean up any new files if saving fails
        for file_info in uploaded_files:
            safe_remove_file(file_info['path'])
        return jsonify({'error': "An error occurred while uploading files. Please try again later."}), 500

@app.route('/remove/<file_id>', methods=['POST'])
def remove_file(file_id):
    """
    Remove a single file from the session and filesystem
    Args:
        file_id (str): Unique identifier of the file to remove
    Returns:
        json: Response with removal status
    """
    files = get_session_files()
    for file in files:
        if file['id'] == file_id:
            safe_remove_file(file['path'])
            files.remove(file)
            session['pdf_files'] = files
            session.modified = True
            return jsonify({'message': 'File removed successfully'})
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/merge', methods=['POST'])
def merge_files():
    """
    Merge all uploaded PDF files into a single PDF
    Returns:
        file: Merged PDF file for download
    """
    files = get_session_files()
    
    if not files:
        return jsonify({'error': 'No files to merge'}), 400

    try:
        pdf_paths = [file['path'] for file in files]
        output = merge_pdfs(pdf_paths)
        
        # Clean up session and temporary files after successful merge
        for file in files:
            safe_remove_file(file['path'])
        session['pdf_files'] = []
        session.modified = True
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
        
    except Exception as e:
        app.logger.error(f"Error during PDF merge: {str(e)}")
        # Clean up files if merge fails
        for file in files:
            safe_remove_file(file['path'])
        session['pdf_files'] = []
        session.modified = True
        return jsonify({'error': "An error occurred while merging files. Please try again later."}), 500

@app.route('/clear', methods=['POST'])
def clear_files():
    """
    Remove all files from the session and filesystem
    Returns:
        json: Response with clear status
    """
    files = get_session_files()
    for file in files:
        safe_remove_file(file['path'])
    session['pdf_files'] = []
    session.modified = True
    return jsonify({'message': 'All files cleared successfully'})

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login
    Returns:
        str: Rendered HTML template for login
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_password_hash = get_user(username)
        if user_password_hash and bcrypt.check_password_hash(user_password_hash, password):
            login_user(User(username))
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """
    Handle user logout
    Returns:
        redirect: Redirect to login page
    """
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """
    User dashboard route
    Returns:
        str: Welcome message for the user
    """
    return f"Welcome, {current_user.id}!"

@app.errorhandler(500)
def internal_server_error(e):
    """
    Handle internal server errors with a generic message
    Args:
        e (Exception): Exception object
    Returns:
        str: Rendered HTML template for error
    """
    app.logger.error(f"Internal Server Error: {str(e)}")
    return render_template('error.html', message="An unexpected error occurred. Please try again later."), 500

@app.errorhandler(404)
def not_found_error(e):
    """
    Handle 404 errors with a generic message
    Args:
        e (Exception): Exception object
    Returns:
        str: Rendered HTML template for error
    """
    app.logger.warning(f"404 Not Found: {str(e)}")
    return render_template('error.html', message="The requested resource was not found."), 404

@app.errorhandler(Exception)
def handle_generic_exception(e):
    """
    Handle generic exceptions with a secure response
    Args:
        e (Exception): Exception object
    Returns:
        str: Rendered HTML template for error
    """
    app.logger.error(f"Unhandled Exception: {str(e)}")
    return render_template('error.html', message="An error occurred. Please contact support if the issue persists."), 500

if __name__ == '__main__':
    # Create uploads and merged directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MERGED_FOLDER'], exist_ok=True)
    app.run(debug=True)
