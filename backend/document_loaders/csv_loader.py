import csv
import io


class CSVLoader:
    def load(self, file_obj) -> str:
        try:
            if isinstance(file_obj, io.BytesIO):
                content = file_obj.read().decode('utf-8')
                file_obj = io.StringIO(content)

            reader = csv.reader(file_obj)
            rows = list(reader)

            text_parts = []
            for row in rows:
                text_parts.append(" | ".join(row))

            return "\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV: {str(e)}")
