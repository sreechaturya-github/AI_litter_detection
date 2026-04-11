from pathlib import Path
import unittest

from src.litterguard.pipeline import LitterGuardPipeline, load_events


class PipelineTests(unittest.TestCase):
    def test_sample_events_escalate_expected_labels(self) -> None:
        events = load_events(Path("sample_data/events.json"))
        incidents = LitterGuardPipeline().process_events(events)

        labels = [incident.label for incident in incidents]
        self.assertIn("littering", labels)
        self.assertIn("unattended_item", labels)
        self.assertIn("illegal_dumping", labels)
        self.assertEqual(len(incidents), 4)


if __name__ == "__main__":
    unittest.main()
