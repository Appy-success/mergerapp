# PDF Merger Application

This is a Flask-based web application for merging PDF files. The application uses:
- **Flask** for the web framework
- **PyPDF2** for PDF manipulation
- **Modern HTML/CSS/JS** for the frontend
- **Font Awesome** for icons

## Features
- Upload multiple PDF files
- Merge PDFs into a single file
- Download the merged PDF
- Error handling for file operations
- Secure file handling

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mergerapp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flask run
   ```

4. Access the application at `http://127.0.0.1:5000`.

## Documentation
- [Usage Examples](./UsageExamples.md)
- [Change Log](./ChangeLog.md)

## Security Considerations
- Ensure uploaded files are validated to prevent malicious content.
- Use secure temporary storage for file operations.

## License
This project is licensed under the MIT License.
