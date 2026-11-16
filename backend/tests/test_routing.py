from app.services.routing_service import routing_service

def test_route_programming():
    res = routing_service.classify("Can you write a Python function with asyncio and debug this syntax error?")
    assert res.category == "programming"
    assert "poolside/laguna-xs-2.1" in res.recommended_model_ids

def test_route_mathematics():
    res = routing_service.classify("Calculate the eigenvalue and matrix determinant for this linear equation")
    assert res.category == "mathematics"
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in res.recommended_model_ids

def test_route_creative():
    res = routing_service.classify("Write a poetic story about a lost astronaut with metaphor and imagery")
    assert res.category == "creative_writing"
    assert "mistralai/mistral-large-4-1t-a52b" in res.recommended_model_ids

def test_route_robotics():
    res = routing_service.classify("How do I configure the PID controller and servo actuator for my ROS robot?")
    assert res.category == "robotics_engineering"
    assert "nvidia/nemotron-3.5-super-vl-120b-a12b" in res.recommended_model_ids
