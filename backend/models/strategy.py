from pydantic import BaseModel


class StrategyInfo(BaseModel):
    name: str
    description: str
    speed: str
    use_case: str
