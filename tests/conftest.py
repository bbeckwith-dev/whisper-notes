import pytest


@pytest.fixture
def sample_config():
    return {
        "vaults": [
            "fantasy-writing",
            "game-development",
            "self-observations",
            "software-engineering",
        ]
    }


@pytest.fixture
def sample_claude_response():
    return (
        "---\n"
        "title: weightlifting-goals\n"
        "date: 2026-03-21\n"
        "processed: 2026-03-21T14:32:00\n"
        "status: raw\n"
        "medium: audio\n"
        "vault: self-observations\n"
        "---\n"
        "\n"
        "## Summary\n"
        "\n"
        "This recording covers a detailed discussion about weightlifting\n"
        "goals for the upcoming quarter. The speaker outlines specific\n"
        "targets for squat and deadlift numbers, discusses current\n"
        "training split adjustments, and reflects on recent form\n"
        "improvements. Key emphasis on progressive overload strategy\n"
        "and the decision to prioritize technique over raw weight.\n"
        "\n"
        "## Cleaned Transcription\n"
        "\n"
        "### Current Goals\n"
        "\n"
        "I want to increase my squat to 300 lbs by the end of the\n"
        "quarter. For deadlifts, I'm going to focus on form over\n"
        "weight for now.\n"
    )
