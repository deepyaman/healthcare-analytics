import pytest

from healthcare_analytics.utils import make_partial, methodcaller


def test_make_partial():
    basetwo = make_partial(int, base=2)
    assert basetwo("10010") == 18
    assert basetwo.__name__ == "int"


@pytest.mark.parametrize("args,kwargs", [([], {}), (["foo"], {"bar": 1})])
def test_methodcaller(mocker, args, kwargs):
    f = methodcaller("name", *args, **kwargs)
    b = mocker.Mock()
    f(b)
    b.name.assert_called_with(*args, **kwargs)
