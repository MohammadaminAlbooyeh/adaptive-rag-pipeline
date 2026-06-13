class RAGException(Exception):
    pass


class RetrievalException(RAGException):
    pass


class GenerationException(RAGException):
    pass


class ConfigurationException(RAGException):
    pass
