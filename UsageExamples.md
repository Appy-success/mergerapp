# Usage Examples

## Uploading PDF Files
1. Navigate to the homepage.
2. Click the "Upload Files" button.
3. Select multiple PDF files from your computer.

## Merging PDFs
1. After uploading files, click the "Merge PDFs" button.
2. Wait for the merging process to complete.
3. Download the merged PDF by clicking the "Download" button.

## Example Code Snippet
Below is an example of how the merging functionality is implemented using PyPDF2:

```python
from PyPDF2 import PdfMerger

def merge_pdfs(file_list):
    merger = PdfMerger()
    for file in file_list:
        merger.append(file)
    output_path = "merged.pdf"
    merger.write(output_path)
    merger.close()
    return output_path
```

## Screenshots
### Homepage
![Homepage](./assets/homepage.png)

### Merging PDFs
![Merging PDFs](./assets/merging.png)

For more details, refer to the [README.md](./README.md).