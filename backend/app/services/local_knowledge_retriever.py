from __future__ import annotations

from pathlib import Path

from app.models.chat import KnowledgeChunk
from app.services.retriever import Retriever


class LocalKnowledgeRetriever:
    """Simple keyword-based retriever for the four-document POC knowledge base."""

    DOMAIN_TERMS = {
        "coffee",
        "machine",
        "broken",
        "fault",
        "equipment",
        "safety",
        "replacement",
        "troubleshooting",
        "smoke",
        "smoking",
        "repair",
        "manager",
        "duty",
        "maintenance",
        "damage",
        "escalation",
        "leakage",
        "wiring",
        "electrical",
        "report",
        "reporting",
        "procedure",
        "burning",
        "spark",
    }

    SYNONYM_MAP = {
        "smoking": "smoke",
        "burning": "smoke",
        "reporting": "report",
    }

    def __init__(self, knowledge_dir: str | Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[3]
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir is not None else project_root / "knowledge"
        self.documents = self._load_documents()

    def _load_documents(self) -> dict[str, str]:
        documents: dict[str, str] = {}
        if not self.knowledge_dir.exists():
            return documents

        for path in sorted(self.knowledge_dir.glob("*.md")):
            documents[path.name] = path.read_text(encoding="utf-8")
        return documents

    def _split_markdown_sections(self, content: str) -> list[tuple[str, str]]:
        """Split Markdown content into logical heading-based sections."""
        lines = content.splitlines()
        sections: list[tuple[str, str]] = []
        current_heading = ""
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("##"):
                if current_heading and current_lines:
                    section_text = "\n".join(current_lines).strip()
                    if section_text:
                        sections.append((current_heading, section_text))
                current_heading = stripped
                current_lines = []
                continue

            if current_heading:
                current_lines.append(line)

        if current_heading and current_lines:
            section_text = "\n".join(current_lines).strip()
            if section_text:
                sections.append((current_heading, section_text))

        if not sections:
            return [("document", content.strip())]

        return [(heading, f"{heading}\n\n{body}".strip()) for heading, body in sections]

    def retrieve(self, query: str) -> list[KnowledgeChunk]:
        """Return the most relevant Markdown sections ranked by domain keyword overlap."""
        normalized_query = self._normalize(query)
        if not normalized_query:
            return []

        query_terms = self._canonicalize_terms(normalized_query)
        relevant_terms = query_terms & self.DOMAIN_TERMS
        if not relevant_terms:
            return []

        scored_sections: list[tuple[float, str, str, str]] = []

        for filename, content in self.documents.items():
            for heading, section_text in self._split_markdown_sections(content):
                normalized_section = self._normalize(section_text)
                normalized_heading = self._normalize(heading)
                section_terms = set(normalized_section.split())
                heading_terms = set(normalized_heading.split())

                overlap = len(relevant_terms & section_terms)
                heading_overlap = len(relevant_terms & heading_terms)
                if overlap == 0 and heading_overlap == 0:
                    continue

                focus_boost = self._section_focus_boost(normalized_heading, normalized_section)
                score = (
                    overlap
                    + heading_overlap * 2
                    + self._phrase_boost(relevant_terms, normalized_section)
                    + self._phrase_boost(relevant_terms, normalized_heading)
                    + focus_boost
                )
                scored_sections.append((score, filename, heading, section_text.strip()))

        scored_sections.sort(key=lambda item: item[0], reverse=True)

        results: list[KnowledgeChunk] = []
        for _, filename, _, section_text in scored_sections[:3]:
            results.append(KnowledgeChunk(content=section_text, source=filename))

        return results

    @classmethod
    def _canonicalize_terms(cls, value: str) -> set[str]:
        tokens = set(value.lower().replace("-", " ").split())
        canonical: set[str] = set()
        for token in tokens:
            canonical.add(cls.SYNONYM_MAP.get(token, token))
        return canonical

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.lower().replace("-", " ").split())

    @staticmethod
    def _phrase_boost(query_terms: set[str], normalized_text: str) -> float:
        phrase_terms = {
            "coffee machine": "coffee machine",
            "broken machine": "broken machine",
            "equipment safety": "equipment safety",
            "equipment replacement": "equipment replacement",
            "reporting a fault": "reporting a fault",
            "reporting a broken coffee machine": "reporting a broken coffee machine",
            "stop using the equipment": "stop using the equipment",
            "stop using the equipment immediately": "stop using the equipment immediately",
            "stop using the machine": "stop using the machine",
            "notify the shift manager": "notify the shift manager",
            "equipment fault log": "equipment fault log",
            "safety concerns": "safety concerns",
            "replacement may be considered when": "replacement may be considered when",
            "smoke coming from equipment": "smoke coming from equipment",
            "smoke": "smoke",
            "burning smell": "burning smell",
            "safety concern": "safety concern",
        }

        boost = 0.0
        for phrase in phrase_terms:
            if phrase in normalized_text and set(phrase.split()) & query_terms:
                boost += 1.0

        if ("smoke" in query_terms or "smoking" in query_terms or "burning" in query_terms) and (
            "smoke" in normalized_text or "burning" in normalized_text or "safety" in normalized_text
        ):
            boost += 2.5

        if "smoke" in query_terms or "smoking" in query_terms or "burning" in query_terms:
            if (
                "immediate safety concerns" in normalized_text
                or "stop using the equipment immediately" in normalized_text
                or "stop using the machine" in normalized_text
            ):
                boost += 4.0

        if "stop using the equipment immediately" in normalized_text:
            boost += 6.0

        return boost

    @staticmethod
    def _section_focus_boost(normalized_heading: str, normalized_section: str) -> float:
        """Prefer action-oriented sections over general introductory content."""
        heading = normalized_heading
        section = normalized_section

        if "purpose" in heading:
            return -4.0

        boost = 0.0
        action_markers = (
            "reporting a fault",
            "reporting",
            "stop use",
            "stop using",
            "stop using the equipment immediately",
            "fault log",
            "immediate safety concerns",
            "authorisation",
            "repair vs replacement",
            "raising a request",
            "safety concerns",
            "safety boundary",
        )
        for marker in action_markers:
            if marker in heading or marker in section:
                boost += 1.5

        if "stop use" in heading or "stop using" in section:
            boost += 6.0

        if "stop using the equipment immediately" in section:
            boost += 8.0

        if "immediate safety concerns" in heading or "immediate safety concerns" in section:
            boost -= 3.0

        if "do not" in section or "must not" in section:
            boost += 1.0

        return boost


def local_knowledge_retriever() -> Retriever:
    """Factory for the local knowledge-base retriever."""
    return LocalKnowledgeRetriever()
