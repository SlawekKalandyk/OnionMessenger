SERVER_DIR_NAME = server
SERVER_DIST_NAME = OnionMessengerServer
CLIENT_DIR_NAME = angular-client

.PHONY: buildpy
buildpy:
	$(MAKE) -C $(SERVER_DIR_NAME) publish

.PHONY: run-electron
run-electron:
	$(MAKE) -C $(CLIENT_DIR_NAME) run-electron

.PHONY: build-all
build-all:
	$(MAKE) buildpy
	$(MAKE) -C $(CLIENT_DIR_NAME) prodbuild