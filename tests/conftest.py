import pytest


@pytest.fixture
def sample_query():
    return "What is Python?"


@pytest.fixture
def sample_document():
    return {"id": "1", "content": "Python is a programming language."}
