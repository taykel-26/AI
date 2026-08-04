from pypdf import PdfReader
def read_file(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    if name.endswith(".txt") or name.endswith(".md"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    return f"Sorry, I can't read {name}. Try a .pdf or .txt file."