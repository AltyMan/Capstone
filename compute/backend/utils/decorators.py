def test_only(func):
    func.__test_only__ = True
    return func
