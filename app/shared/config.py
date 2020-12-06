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

class TorConfiguration(BaseConfiguration):
    
    key_file_name = 'key'

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


class OSNotSupportedError(Exception):
    pass

class DatabaseConfiguration(BaseConfiguration):
    @staticmethod
    def get_database_path():
        pass