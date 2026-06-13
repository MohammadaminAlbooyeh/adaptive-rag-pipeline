from typing import List


class BatchLoader:
    def __init__(self, loaders: List):
        self.loaders = loaders

    async def load_all(self, file_paths: List[str]) -> List[dict]:
        return []
