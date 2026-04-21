.PHONY: build
build: ##@local Build selected package(s) with poetry
build:
	@for pkg in $(SELECTED_PKGS); do \
		echo "Building $$pkg..."; \
		cd $(SRC_DIR)/$$pkg && ${POETRY} build && cd -; \
	done
