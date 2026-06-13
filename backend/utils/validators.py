def validate_query(query: str) -> bool:
    return bool(query and query.strip())


def validate_file_extension(filename: str) -> bool:
    allowed = {".pdf", ".docx", ".txt", ".csv"}
    return any(filename.lower().endswith(ext) for ext in allowed)
