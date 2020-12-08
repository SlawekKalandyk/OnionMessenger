APP_BUILD_DIR = ../appbuild

.PHONY: run-electron
run-electron:
	npm run electron-build

.PHONY: prodbuild
prodbuild:
	npm run prodbuild

.PHONY: package-electron
package-electron:
	electron-packager . --overwrite --executable-name=OnionMessenger --ignore=.gitignore