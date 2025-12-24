from pathlib import Path


def test_persona_protocol_present():
    path = Path(__file__).resolve().parents[1] / ".github" / "copilot-instructions.md"
    assert path.exists(), ".github/copilot-instructions.md must exist"
    text = path.read_text(encoding="utf-8")

    # Required identity and model rules
    assert "Persona Protocol" in text, "Persona Protocol section missing"
    assert "GitHub Copilot" in text, "Identity must declare GitHub Copilot"
    assert "GPT-5" in text, "Model disclosure must state GPT-5"

    # Safety and content policy
    assert "Microsoft content policies" in text, "Must follow Microsoft content policies"
    assert "Sorry, I can't assist with that." in text, "Harmful content response must be exact"

    # Copyright guidance
    assert "violates copyrights" in text or "copyright" in text.lower(), "Copyright avoidance must be documented"

    # Tone and formatting
    assert "No emoji" in text or "NO EMOJI" in text or "DD-001" in text, "No emoji rule must be present"


def test_persona_protocol_no_heavy_formatting_examples():
    path = Path(__file__).resolve().parents[1] / ".github" / "copilot-instructions.md"
    text = path.read_text(encoding="utf-8")
    # Ensure the file encourages concise, direct, friendly tone
    assert "concise, direct, and friendly" in text, "Tone guidance missing"
