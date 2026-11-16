from app.services.routing_service import routing_service

def test_route_programming():
    res = routing_service.classify("Can you write a Python function with asyncio and debug this syntax error?")
    assert res.category == "programming"
    assert "anthropic/claude-sonnet-5.5" in res.recommended_model_ids

def test_route_mathematics():
    res = routing_service.classify("Calculate the eigenvalue and matrix determinant for this linear equation")
    assert res.category == "mathematics"
    assert "openai/gpt-5" in res.recommended_model_ids

def test_route_science():
    res = routing_service.classify("Formulate a hypothesis regarding thermodynamic entropy and physics")
    assert res.category == "scientific_reasoning"
    assert "openai/4-hydrogen" in res.recommended_model_ids

def test_route_robotics():
    res = routing_service.classify("How do I configure the PID controller and servo actuator for my ROS robot?")
    assert res.category == "robotics_engineering"
    assert "openai/4-argon" in res.recommended_model_ids
