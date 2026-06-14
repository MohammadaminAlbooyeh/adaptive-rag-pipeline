from typing import List
import pypdf


class PDFLoader:
    def load(self, file_obj) -> str:
        try:
            reader = pypdf.PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise RuntimeError(f"Failed to load PDF: {str(e)}")
