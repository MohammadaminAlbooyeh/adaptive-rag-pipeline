from backend.adaptive_rag.router.query_classifier import ClassificationResult


class TestQueryClassifier:
    def test_classify_factual_simple(self, query_classifier):
        result = query_classifier.classify("What is Python?")
        assert isinstance(result, ClassificationResult)
        assert result.query_type == "factual"
        assert result.complexity == "simple"
        assert result.needs_docs is True
        assert result.needs_web is False
        assert result.is_time_sensitive is False
        assert result.needs_graph is False

    def test_classify_comparative(self, query_classifier, sample_query_comparative):
        result = query_classifier.classify(sample_query_comparative)
        assert result.query_type == "comparative"
        assert result.needs_docs is True

    def test_classify_comparative_variants(self, query_classifier):
        for kw in ["vs", "versus", "difference", "better", "worse"]:
            result = query_classifier.classify(f"{kw} A and B")
            assert result.query_type == "comparative", f"Failed for keyword '{kw}'"

    def test_classify_procedural(self, query_classifier, sample_query_procedural):
        result = query_classifier.classify(sample_query_procedural)
        assert result.query_type == "procedural"

    def test_classify_procedural_variants(self, query_classifier):
        for kw in ["steps", "instructions", "guide", "process"]:
            result = query_classifier.classify(f"What are the {kw} for X")
            assert result.query_type == "procedural", f"Failed for keyword '{kw}'"

    def test_classify_exploratory(self, query_classifier):
        # "explain" matches before "how" since the test keyword "explain" is
        # checked before procedural keywords in _determine_type
        result = query_classifier.classify("Explain neural networks")
        assert result.query_type == "exploratory"

    def test_classify_exploratory_variants(self, query_classifier):
        for kw in ["why", "describe", "tell me about"]:
            result = query_classifier.classify(f"{kw} something")
            assert result.query_type == "exploratory", f"Failed for keyword '{kw}'"

    def test_classify_opinion(self, query_classifier, sample_query_opinion):
        result = query_classifier.classify(sample_query_opinion)
        assert result.query_type == "opinion"

    def test_classify_opinion_variants(self, query_classifier):
        for kw in ["think", "believe", "should", "recommend"]:
            result = query_classifier.classify(f"What do you {kw} about X")
            assert result.query_type == "opinion", f"Failed for keyword '{kw}'"

    def test_classify_type_precedence(self, query_classifier):
        # comparative keyword should take precedence over procedural
        result = query_classifier.classify("Compare how to install Python versus Java")
        assert result.query_type == "comparative"

    def test_complexity_simple(self, query_classifier):
        assert query_classifier.classify("What is Python?").complexity == "simple"

    def test_complexity_moderate_by_word_count(self, query_classifier):
        result = query_classifier.classify(
            "What are the key differences between Python and JavaScript for data science tasks"
        )
        assert result.complexity == "moderate"

    def test_complexity_moderate_by_conjunction(self, query_classifier):
        result = query_classifier.classify("What is Python and how does it compare")
        assert result.complexity == "moderate"

    def test_complexity_complex_by_word_count(self, query_classifier):
        result = query_classifier.classify(
            "What are the key differences between Python and JavaScript "
            "for data science tasks and how do they compare in terms of performance"
        )
        assert result.complexity == "complex"

    def test_complexity_complex_by_conjunctions(self, query_classifier):
        result = query_classifier.classify(
            "Compare Python and Java and JavaScript and C++ and Go"
        )
        assert result.complexity == "complex"

    def test_time_sensitive_flag(self, query_classifier):
        result = query_classifier.classify("latest news about AI today")
        assert result.is_time_sensitive is True
        assert result.needs_web is True
        assert result.needs_docs is False

    def test_time_sensitive_keywords(self, query_classifier):
        for kw in [
            "today",
            "yesterday",
            "latest",
            "recent",
            "now",
            "current",
            "breaking",
            "news",
        ]:
            result = query_classifier.classify(f"What is the {kw} update")
            assert result.is_time_sensitive is True, f"Failed for keyword '{kw}'"
            assert result.needs_web is True, f"Failed for keyword '{kw}'"

    def test_needs_graph_flag(self, query_classifier, sample_query_graph):
        result = query_classifier.classify(sample_query_graph)
        assert result.needs_graph is True

    def test_graph_keywords(self, query_classifier):
        for kw in ["relationship", "connected", "associated", "entity", "entities"]:
            result = query_classifier.classify(f"What are the {kw} in this data")
            assert result.needs_graph is True, f"Failed for keyword '{kw}'"

    def test_neither_docs_nor_web(self, query_classifier):
        result = query_classifier.classify("What is 2+2?")
        assert result.needs_docs is True
        assert result.needs_web is False

    def test_mixed_flags(self, query_classifier):
        result = query_classifier.classify(
            "Latest relationships between entities in AI research"
        )
        assert result.needs_web is True
        assert result.needs_graph is True
        assert result.is_time_sensitive is True
        assert result.needs_docs is False

    def test_empty_query(self, query_classifier):
        result = query_classifier.classify("")
        assert result.query_type == "factual"
        assert result.complexity == "simple"
        assert result.needs_docs is True
        assert result.needs_web is False

    def test_case_insensitivity(self, query_classifier):
        result_upper = query_classifier.classify("COMPARE Python and Java")
        result_lower = query_classifier.classify("compare Python and Java")
        assert result_upper.query_type == result_lower.query_type

    def test_keyword_in_long_string(self, query_classifier):
        # "tell me about" is exploratory and checked before opinion
        result = query_classifier.classify(
            "I was wondering if you could tell me about the best way to think about Python?"
        )
        assert result.query_type == "exploratory"

    def test_opinion_without_exploratory_keywords(self, query_classifier):
        result = query_classifier.classify("What do you think is the best framework")
        assert result.query_type == "opinion"
