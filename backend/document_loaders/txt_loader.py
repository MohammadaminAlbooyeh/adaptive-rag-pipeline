class TXTLoader:
    def load(self, file_obj) -> str:
        try:
            content = file_obj.read()
            if isinstance(content, bytes):
                return content.decode('utf-8', errors='ignore')
            return content
        except Exception as e:
            raise RuntimeError(f"Failed to load TXT: {str(e)}")
