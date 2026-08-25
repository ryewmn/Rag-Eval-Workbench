from __future__ import annotations

import unittest

from rag_eval_workbench.models import Document
from rag_eval_workbench.retriever import BM25Retriever


class RetrieverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.documents = [
            Document("a", "Apple guide", "apple orchard fruit", {}),
            Document("b", "Banana guide", "banana yellow fruit", {}),
            Document("c", "Cherry guide", "cherry red fruit", {}),
        ]
        self.retriever = BM25Retriever(self.documents)

    def test_returns_relevant_document_first(self) -> None:
        self.assertEqual(self.retriever.search("yellow banana", k=2)[0].document.id, "b")

    def test_ties_are_broken_by_document_id(self) -> None:
        ids = [result.document.id for result in self.retriever.search("fruit", k=3)]
        self.assertEqual(ids, ["a", "b", "c"])

    def test_empty_token_query_returns_no_results(self) -> None:
        self.assertEqual(self.retriever.search("!!!", k=2), [])

    def test_invalid_k_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.retriever.search("fruit", k=0)


if __name__ == "__main__":
    unittest.main()
