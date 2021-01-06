import os
import platform

class BaseConfiguration:
    app_local_data_directory = 'OnionMessenger'

    @staticmethod
    def _get_local_app_full_path():
        if platform.system() == 'Windows':
            local_app_data = os.getenv('LOCALAPPDATA')
            return os.path.join(local_app_data, BaseConfiguration.app_local_data_directory)
        raise OSNotSupportedError()


class OSNotSupportedError(Exception):
    pass


class TorConfiguration(BaseConfiguration):
    key_file_name = 'key'
    service_id_file_name = 'service_id'

    @staticmethod
    def get_tor_server_port():
        return 39123

    @staticmethod
    def get_tor_executable_path():
        return 'D:\\Programming\\tor-win32-0.4.4.5\\Tor\\tor.exe'

    @staticmethod
    def save_hidden_service_key(key: str):
        if not os.path.exists(TorConfiguration._get_local_app_full_path()):
            os.makedirs(TorConfiguration._get_local_app_full_path())

        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.key_file_name), 'w+') as key_file:
            key_file.write(key)

            
    @staticmethod
    def get_hidden_service_key():
        if not os.path.exists(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.key_file_name)):
            return None
        
        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.key_file_name), 'r') as key_file:
            return key_file.readline()


    @staticmethod
    def save_hidden_service_id(service_id: str):
        if not os.path.exists(TorConfiguration._get_local_app_full_path()):
            os.makedirs(TorConfiguration._get_local_app_full_path())

        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.service_id_file_name), 'w+') as service_id_file:
            service_id_file.write(service_id)

    @staticmethod
    def get_hidden_service_id():
        if not os.path.exists(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.service_id_file_name)):
            return None
        
        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.service_id_file_name), 'r') as service_id_file:
            return service_id_file.readline()


class DatabaseConfiguration(BaseConfiguration):
    database_name = 'onion_messenger.sqlite'

    @staticmethod
    def get_database_path():
        if not os.path.exists(DatabaseConfiguration._get_local_app_full_path()):
            os.makedirs(DatabaseConfiguration._get_local_app_full_path())

        return os.path.join(DatabaseConfiguration._get_local_app_full_path(), DatabaseConfiguration.database_name)


class AuthenticationConfiguration(BaseConfiguration):
    signature_private_key_file_name = 'signature_private_key'
    signature_public_key_file_name = 'signature_public_key'
    signature_private_key = None
    signature_public_key = None

    @staticmethod
    def save_signature_private_key(new_signature_private_key):
        with open(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_private_key_file_name), 'w+') as signature_private_key_file:
            signature_private_key_file.write(new_signature_private_key)
            AuthenticationConfiguration.signature_private_key = new_signature_private_key

    @staticmethod
    def get_signature_private_key():
        if AuthenticationConfiguration.signature_private_key:
            return AuthenticationConfiguration.signature_private_key

        if not os.path.exists(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_private_key_file_name)):
            return None

        with open(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_private_key_file_name), 'r') as signature_private_key_file:
            AuthenticationConfiguration.signature_private_key = signature_private_key_file.readline()
            return AuthenticationConfiguration.signature_private_key

    @staticmethod
    def save_signature_public_key(new_signature_public_key):
        with open(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_public_key_file_name), 'w+') as signature_public_key_file:
            signature_public_key_file.write(new_signature_public_key)
            AuthenticationConfiguration.signature_public_key = new_signature_public_key

    @staticmethod
    def get_signature_public_key():
        if AuthenticationConfiguration.signature_public_key:
            return AuthenticationConfiguration.signature_public_key
        
        if not os.path.exists(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_public_key_file_name)):
            return None

        with open(os.path.join(AuthenticationConfiguration._get_local_app_full_path(), AuthenticationConfiguration.signature_public_key_file_name), 'r') as signature_public_key_file:
            AuthenticationConfiguration.signature_public_key = signature_public_key_file.readline()
            return AuthenticationConfiguration.signature_public_key