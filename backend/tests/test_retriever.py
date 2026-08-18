from app.services.local_knowledge_retriever import LocalKnowledgeRetriever


def test_retriever_finds_broken_machine_procedure() -> None:
    retriever = LocalKnowledgeRetriever()

    results = retriever.retrieve("What is the procedure for reporting a broken coffee machine?")

    assert results
    first = results[0]
    assert first.source == "coffee_machine_broken.md"
    assert "Reporting a Fault" in first.content
    assert "Notify the" in first.content
    assert "Equipment Fault Log" in first.content
    assert "Stop using the machine" in first.content or "follow the" in first.content.lower()


def test_retriever_finds_safety_document_for_safety_query() -> None:
    retriever = LocalKnowledgeRetriever()

    results = retriever.retrieve("The coffee machine is smoking")

    assert results
    first = results[0]
    assert first.source == "equiptment_safety_escalation.md"
    assert "Stop using the equipment immediately" in first.content or "Safety concerns" in first.content


def test_retriever_finds_replacement_document_for_equipment_query() -> None:
    retriever = LocalKnowledgeRetriever()

    results = retriever.retrieve("How do I get a replacement machine?")

    assert results
    first = results[0]
    assert first.source == "equiptment_replacement.md"
    assert "Replacement may be considered when" in first.content or "Authorisation" in first.content


def test_retriever_ignores_unrelated_queries() -> None:
    retriever = LocalKnowledgeRetriever()

    results = retriever.retrieve("what is the weather in london today")

    assert results == []


def test_retriever_preserves_source_filenames() -> None:
    retriever = LocalKnowledgeRetriever()

    results = retriever.retrieve("coffee machine is broken")

    assert results
    assert {result.source for result in results}.issubset({
        "coffee_machine_broken.md",
        "equiptment_replacement.md",
        "coffee_machine_troubleshooting.md",
    })
