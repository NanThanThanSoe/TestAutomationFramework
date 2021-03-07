import pytest

def test_demo_0(ping):
    rhost_is_up = ping('10.13.201.18','22')
    assert rhost_is_up, "The system is offline"

  
    