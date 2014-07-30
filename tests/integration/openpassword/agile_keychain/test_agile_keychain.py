import os
from nose.tools import *
import shutil
from openpassword import AgileKeychain


class AgileKeychainTest:
    _temporary_path = "somefolder"
    _password = "somepassword"

    def it_creates_agile_keychain_folder_structure_on_initialisation(self):
        self._initialise_agile_keychain()

        assert os.path.exists(self._temporary_path) and os.path.isdir(self._temporary_path)

        data_default_dir = os.path.join(self._temporary_path, "data", "default")
        assert os.path.exists(data_default_dir) and os.path.isdir(data_default_dir)

        keys_file = os.path.join(data_default_dir, '1password.keys')
        assert os.path.exists(keys_file) and os.path.isfile(keys_file)

        contents_file = os.path.join(data_default_dir, 'contents.js')
        assert os.path.exists(contents_file) and os.path.isfile(contents_file)

        encryption_keys_file = os.path.join(data_default_dir, 'encryptionKeys.js')
        assert os.path.exists(encryption_keys_file) and os.path.isfile(encryption_keys_file)

    def it_stores_agile_keychain_password_on_initialisation(self):
        self._initialise_agile_keychain()

        data_default_dir = os.path.join(self._temporary_path, "data", "default")
        encryption_keys_file = open(os.path.join(data_default_dir, 'encryptionKeys.js'), "r")

        assert self._password in encryption_keys_file.read()
        encryption_keys_file.close()

    def it_verifies_password(self):
        self._initialise_agile_keychain()

        try:
            self._agile_keychain.unlock(self._password)
        except:
            assert False

    def _initialise_agile_keychain(self):
        self._agile_keychain = AgileKeychain(self._temporary_path)
        self._agile_keychain.initialise(self._password)
        self.teardown = self._path_clean

    def _path_clean(self):
        shutil.rmtree(self._temporary_path)

    def it_is_created_initialised_with_path_to_existing_keychain(self):
        agile_keychain = AgileKeychain(os.path.join('tests', 'fixtures', 'test.agilekeychain'))
        eq_(agile_keychain.is_initialised(), True)

    def it_is_created_non_initialised_with_path_to_non_existing_keychain(self):
        agile_keychain = AgileKeychain("nonexistingfolder")
        eq_(agile_keychain.is_initialised(), False)

    def it_creates_new_items_on_the_keychain(self):
        agile_keychain = AgileKeychain(os.path.join('tests', 'fixtures', 'test.agilekeychain'))
        agile_keychain.append({'id': '79cd94b00ab34d209d62e487e77965a5'})

        assert os.path.exists(os.path.join('tests', 'fixtures', 'test.agilekeychain', 'data', 'default',
                                           '79cd94b00ab34d209d62e487e77965a5.1password')) is True
        os.remove(os.path.join('tests', 'fixtures', 'test.agilekeychain', 'data', 'default',
                               '79cd94b00ab34d209d62e487e77965a5.1password'))
