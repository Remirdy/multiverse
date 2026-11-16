from app.providers.registry import model_registry

def test_registry_has_models():
    models = model_registry.list_all()
    assert len(models) >= 6
    ids = [m.id for m in models]
    assert "poolside/laguna-xs-2.1" in ids
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in ids
    assert "nvidia/nemotron-3-ultra-550b-a55b" in ids
    assert "nvidia/nemotron-3.5-bolt-e4b" in ids

def test_default_models():
    defaults = model_registry.get_default_model_ids()
    assert len(defaults) >= 2
    assert "poolside/laguna-xs-2.1" in defaults
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in defaults

def test_model_metadata():
    model = model_registry.get("poolside/laguna-xs-2.1")
    assert model is not None
    assert "Sonnet" in model.category
    assert "programming" in model.tags
