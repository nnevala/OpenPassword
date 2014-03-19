class Keychain(object):
    def __init__(self):
        self.locked = True
        self._items = []

    def unlock(self, password):
        self.locked = False

    def lock(self):
        self.locked = True

    def is_locked(self):
        return self.locked

    def __iter__(self):
        return iter(self._items)
