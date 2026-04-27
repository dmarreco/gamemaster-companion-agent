import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from new_campaign import create_campaign, VALID_RULESETS


def test_creates_required_directories(tmp_path):
    create_campaign("test-campaign", "dnd5e-2024", campaigns_dir=tmp_path)
    base = tmp_path / "test-campaign"
    assert (base / "sessions").is_dir()
    assert (base / "world").is_dir()
    assert (base / "characters").is_dir()


def test_creates_required_files(tmp_path):
    create_campaign("test-campaign", "dnd5e-2024", campaigns_dir=tmp_path)
    base = tmp_path / "test-campaign"
    assert (base / "ruleset.txt").exists()
    assert (base / "campaign.md").exists()
    assert (base / "world" / "npcs.md").exists()
    assert (base / "world" / "locations.md").exists()
    assert (base / "world" / "factions.md").exists()


def test_ruleset_txt_contains_correct_value(tmp_path):
    create_campaign("my-adventure", "pathfinder2e", campaigns_dir=tmp_path)
    content = (tmp_path / "my-adventure" / "ruleset.txt").read_text().strip()
    assert content == "pathfinder2e"


def test_rejects_invalid_ruleset(tmp_path):
    with pytest.raises(ValueError, match="Unknown ruleset"):
        create_campaign("bad", "dnd3e", campaigns_dir=tmp_path)


def test_rejects_existing_campaign(tmp_path):
    create_campaign("existing", "dnd5e-2024", campaigns_dir=tmp_path)
    with pytest.raises(FileExistsError):
        create_campaign("existing", "dnd5e-2024", campaigns_dir=tmp_path)


def test_valid_rulesets_list():
    assert "dnd5e-2024" in VALID_RULESETS
    assert "dnd5e-2014" in VALID_RULESETS
    assert "pathfinder2e" in VALID_RULESETS
