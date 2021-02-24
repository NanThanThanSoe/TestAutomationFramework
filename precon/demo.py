import pytest
import requests

@pytest.fixture
def hello():
    response = requests.get('https://httpbin.org/ip')

    print("Hello Nan")
    print('Your IP is {0}'.format(response.json()['origin']))

def f():
    return 3


def test_function():
    assert f() == 4

def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
    assert set1 == set2