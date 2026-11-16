from app.providers.registry import model_registry

def test_registry_has_models():
    models = model_registry.list_all()
    assert len(models) >= 6
    ids = [m.id for m in models]
    assert "openai/gpt-5" in ids
    assert "anthropic/claude-sonnet-5.5" in ids
    assert "google/gemini-3.8-flash" in ids
    assert "openai/4-hydrogen" in ids
    assert "openai/4-argon" in ids

def test_default_models():
    defaults = model_registry.get_default_model_ids()
    assert len(defaults) >= 2
    assert "anthropic/claude-sonnet-5.5" in defaults
    assert "openai/gpt-5" in defaults

def test_model_metadata():
    model = model_registry.get("anthropic/claude-sonnet-5.5")
    assert model is not None
    assert model.category == "Agentic Coding & Software"
    assert "programming" in model.tags
