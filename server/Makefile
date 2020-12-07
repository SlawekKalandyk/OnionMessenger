SERVER_DIST_NAME = OnionMessenger
APP_BUILD_DIR = ../appbuild

.PHONY: publish
publish:
	pipenv run pyinstaller --onefile --name ${SERVER_DIST_NAME} --specpath ${APP_BUILD_DIR}/spec --distpath ${APP_BUILD_DIR}/dist --workpath ${APP_BUILD_DIR}/build outer_script.py