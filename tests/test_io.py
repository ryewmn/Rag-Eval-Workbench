from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag_eval_workbench.io import load_documents, load_queries, validate_relevance
from rag_eval_workbench.models import DatasetError


class DatasetValidationTest(unittest.TestCase):
    def test_duplicate_document_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.jsonl"
            path.write_text(
                '{"id":"x","title":"One","text":"Body"}\n'
                '{"id":"x","title":"Two","text":"Body"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DatasetError, "duplicate id"):
                load_documents(path)

    def test_unknown_relevance_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.jsonl"
            queries = root / "queries.jsonl"
            corpus.write_text('{"id":"x","title":"One","text":"Body"}\n', encoding="utf-8")
            queries.write_text(
                '{"id":"q","query":"Question","relevant_ids":["missing"],'
                '"reference_answer":"Answer"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DatasetError, "unknown document ids"):
                validate_relevance(load_documents(corpus), load_queries(queries))


if __name__ == "__main__":
    unittest.main()
