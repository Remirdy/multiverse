from app.providers.registry import model_registry

def test_registry_has_models():
    models = model_registry.list_all()
    assert len(models) >= 6
    ids = [m.id for m in models]
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in ids
    assert "mistralai/mistral-large-4-1t-a52b" in ids
    assert "poolside/laguna-xs-2.1" in ids

def test_default_models():
    defaults = model_registry.get_default_model_ids()
    assert len(defaults) >= 2
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in defaults

def test_model_metadata():
    model = model_registry.get("poolside/laguna-xs-2.1")
    assert model is not None
    assert model.category == "Programming"
    assert "programming" in model.tags
