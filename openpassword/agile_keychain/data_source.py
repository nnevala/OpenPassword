import gc
from time import time

from openpassword import abstract
from openpassword.exceptions import KeyValidationException, IncorrectPasswordException, \
    UnauthenticatedDataSourceException
from openpassword.agile_keychain._manager._file_system_manager import FileSystemManager
from openpassword.agile_keychain._manager._key_manager import KeyManager
from openpassword.agile_keychain._manager._item_manager import ItemManager
from openpassword.agile_keychain._crypto import create_key, decrypt_key, encrypt_key, \
    decrypt_item, encrypt_item, generate_id
from openpassword.agile_keychain.agile_keychain_item import AgileKeychainItem

DEFAULT_ITERATIONS = 25000


class DataSource(abstract.DataSource):
    def __init__(self, path):
        self._file_system_manager = FileSystemManager(path)
        self._key_manager = KeyManager(path)
        self._item_manager = ItemManager(path)
        self._keys = []

    def initialise(self, password, config=None):
        self._file_system_manager.initialise()

        iterations = self._read_iterations_from_config(config)
        self._key_manager.save_key(create_key(password, 'SL3', iterations))
        self._key_manager.save_key(create_key(password, 'SL5', iterations))

    def is_initialised(self):
        return self._file_system_manager.is_initialised()

    def authenticate(self, password):
        try:
            self._keys = [decrypt_key(key, password) for key in self._key_manager.get_keys()]
        except KeyValidationException:
            raise IncorrectPasswordException

    def is_authenticated(self):
        if len(self._keys) == 0:
            return False

        for key in self._keys:
            if key.key is None:
                return False

        return True

    def deauthenticate(self):
        self._keys = []
        gc.collect()

    def set_password(self, password):
        for key in self._keys:
            self._key_manager.save_key(encrypt_key(key, password))

    def create_item(self, data=None):
        if type(data) is not dict:
            data = {}

        item = self._get_default_item()
        item.update(data)
        item['uuid'] = generate_id()
        item['keyID'] = self._get_default_key().identifier

        return AgileKeychainItem(item)

    def save_item(self, decrypted_item):
        self._assert_data_source_is_authenticated()

        encrypted_item = encrypt_item(decrypted_item, self._get_key_for_item(decrypted_item))
        self._item_manager.save_item(encrypted_item)

    def get_item_by_id(self, item_id):
        self._assert_data_source_is_authenticated()

        encrypted_item = self._item_manager.get_by_id(item_id)
        return decrypt_item(encrypted_item, self._get_key_for_item(encrypted_item))

    def get_all_items(self):
        self._assert_data_source_is_authenticated()

        items = []
        for encrypted_item in self._item_manager.get_all_items():
            key = self._get_key_for_item(encrypted_item)
            items.append(decrypt_item(encrypted_item, key))

        return items

    def _assert_data_source_is_authenticated(self):
        if self.is_authenticated() is False:
            raise UnauthenticatedDataSourceException()

    def _get_key_for_item(self, item):
        if item['openContents'] is None:
            return self._get_default_key()

        if 'securityLevel' not in item['openContents']:
            return self._get_default_key()

        return self._get_key_by_security_level(item['openContents']['securityLevel'])

    def _get_key_by_security_level(self, security_level):
        return [key for key in self._keys if key.level == security_level][0]

    def _get_default_key(self):
        return self._get_key_by_security_level('SL5')

    def _read_iterations_from_config(self, config):
        if type(config) is not dict:
            return DEFAULT_ITERATIONS

        if 'iterations' in config:
            return config['iterations']

        return DEFAULT_ITERATIONS

    def _get_default_item(self):
        return {
            'createdAt': time(),
            'location': '',
            'locationKey': '',
            'typeName': 'passwords.Password',
            'title': 'Untitled'
        }
