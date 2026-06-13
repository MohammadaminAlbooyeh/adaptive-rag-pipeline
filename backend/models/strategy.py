from pydantic import BaseModel
from typing import List


class StrategyInfo(BaseModel):
    name: str
    description: str
    speed: str
    use_case: str
