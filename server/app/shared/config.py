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
    private_key_file_name = 'private_key'
    public_key_file_name = 'public_key'
    service_id_file_name = 'service_id'
    _private_key = None
    _public_key = None
    _service_id = None

    @staticmethod
    def get_tor_server_port():
        return 39123

    @staticmethod
    def get_tor_executable_path():
        return 'D:\\Programming\\tor-win32-0.4.4.5\\Tor\\tor.exe'

    @staticmethod
    def save_hidden_service_private_key(key: str):
        if not os.path.exists(TorConfiguration._get_local_app_full_path()):
            os.makedirs(TorConfiguration._get_local_app_full_path())

        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.private_key_file_name), 'w+') as key_file:
            key_file.write(key)
            TorConfiguration._private_key = key
            
    @staticmethod
    def get_hidden_service_private_key():
        if TorConfiguration._private_key:
            return TorConfiguration._private_key

        if not os.path.exists(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.private_key_file_name)):
            return None
        
        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.private_key_file_name), 'r') as key_file:
            return key_file.readline()

    @staticmethod
    def save_hidden_service_public_key(key: str):
        if not os.path.exists(TorConfiguration._get_local_app_full_path()):
            os.makedirs(TorConfiguration._get_local_app_full_path())

        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.public_key_file_name), 'w+') as key_file:
            key_file.write(key)
            TorConfiguration._public_key = key
            
    @staticmethod
    def get_hidden_service_public_key():
        if TorConfiguration._public_key:
            return TorConfiguration._public_key

        if not os.path.exists(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.public_key_file_name)):
            return None
        
        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.public_key_file_name), 'r') as key_file:
            return key_file.readline()

    @staticmethod
    def save_hidden_service_id(service_id: str):
        if TorConfiguration._service_id:
            return TorConfiguration._service_id

        if not os.path.exists(TorConfiguration._get_local_app_full_path()):
            os.makedirs(TorConfiguration._get_local_app_full_path())

        with open(os.path.join(TorConfiguration._get_local_app_full_path(), TorConfiguration.service_id_file_name), 'w+') as service_id_file:
            service_id_file.write(service_id)
            TorConfiguration._service_id = service_id

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