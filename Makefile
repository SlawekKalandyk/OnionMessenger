SERVER_DIR_NAME = server
SERVER_DIST_NAME = OnionMessengerServer
CLIENT_DIR_NAME = angular-client

.PHONY: buildpy
buildpy:
	$(MAKE) -C $(SERVER_DIR_NAME) publish

.PHONY: run-electron
run-electron:
	$(MAKE) buildpy
	$(MAKE) -C $(CLIENT_DIR_NAME) run-electron

.PHONY: build-all
build-all:
	$(MAKE) buildpy
	$(MAKE) -C $(CLIENT_DIR_NAME) prodbuild
	cp ./appbuild/dist/$(SERVER_DIST_NAME).exe ./$(CLIENT_DIR_NAME)/dist
	$(MAKE) -C $(CLIENT_DIR_NAME) package-electron