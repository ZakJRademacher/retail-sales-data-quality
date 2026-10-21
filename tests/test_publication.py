"""Regression tests for complete-version publication and failure recovery."""
import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import closing

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import pipeline
from publication import current_output


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root/"input.csv"
        self.output = self.root/"results"
        self.notes = self.root/"notes.csv"
        self.write_source()

    def tearDown(self):
        self.temp.cleanup()

    def write_source(self):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(pipeline.FIELDS)
            writer.writerow(["100", "P1", "Test", "2", "12/01/2011 08:00", "10", "C1", "United Kingdom"])

    def run_pipeline(self):
        return pipeline.run(self.source, self.output)

    def published_bytes(self):
        return {p.name: p.read_bytes() for p in current_output(self.output).iterdir() if p.is_file()}

    def baseline(self):
        self.run_pipeline()
        return (self.output/"latest.json").read_bytes(), self.published_bytes()

    def assert_preserved(self, baseline):
        self.assertEqual((self.output/"latest.json").read_bytes(), baseline[0])
        self.assertEqual(self.published_bytes(), baseline[1])
        self.assertFalse((self.output/".refresh.lock").exists())

    def test_bad_source_preserves_all_published_files(self):
        before = self.baseline()
        self.source.write_text("wrong_header\nbad\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_pipeline()
        self.assert_preserved(before)

    def test_failed_export_preserves_all_published_files(self):
        before = self.baseline()
        with patch("pipeline.export_query", side_effect=OSError("simulated export failure")):
            with self.assertRaises(OSError):
                self.run_pipeline()
        self.assert_preserved(before)

    def test_failed_database_preserves_all_published_files(self):
        before = self.baseline()
        with patch("pipeline.sqlite3.connect", side_effect=sqlite3.OperationalError("simulated database failure")):
            with self.assertRaises(sqlite3.OperationalError):
                self.run_pipeline()
        self.assert_preserved(before)

    def test_failed_pointer_publication_preserves_all_published_files(self):
        before = self.baseline()
        with patch("publication.os.replace", side_effect=OSError("simulated publication failure")):
            with self.assertRaises(OSError):
                self.run_pipeline()
        self.assert_preserved(before)

    def test_repeat_run_publishes_complete_nonaccumulating_results(self):
        first = self.run_pipeline()
        old = current_output(self.output)
        second = self.run_pipeline()
        new = current_output(self.output)
        self.assertNotEqual(old, new)
        self.assertTrue((old/"analysis.json").is_file())
        self.assertEqual(first["metrics"], second["metrics"])
        self.assertEqual(json.loads((new/"analysis.json").read_text())["metrics"], second["metrics"])
        with closing(sqlite3.connect(new/"retail.sqlite")) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM lines").fetchone()[0], 1)

    def test_overlapping_refresh_is_blocked(self):
        self.run_pipeline()
        before = (self.output/"latest.json").read_bytes()
        (self.output/".refresh.lock").write_text("other refresh")
        with self.assertRaises(RuntimeError):
            self.run_pipeline()
        self.assertEqual((self.output/"latest.json").read_bytes(), before)
        self.assertTrue((self.output/".refresh.lock").exists())

    def test_reader_rejects_invalid_pointer(self):
        self.output.mkdir()
        (self.output/"latest.json").write_text('{"contract_version":1,"snapshot":"../../outside"}')
        with self.assertRaises(ValueError):
            current_output(self.output)

    def test_legacy_reference_remains_readable(self):
        self.output.mkdir()
        self.assertEqual(current_output(self.output), self.output.resolve())


if __name__ == "__main__":
    unittest.main()
