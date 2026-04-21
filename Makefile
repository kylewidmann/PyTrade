SHELL := /bin/bash -e -o pipefail
export PATH := $(HOME)/.local/bin:$(PATH)

PROJECT ?= pytrade
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD | tr '/' '-')
BUILD_NUMBER ?= 0
POETRY ?= poetry
SRC_DIR := src

# Auto-discover packages under src/
PACKAGES := $(shell ls $(SRC_DIR))

# Package filter: "make <cmd> pytrade" selects one package
PKG_FILTER := $(filter $(PACKAGES),$(MAKECMDGOALS))
SELECTED_PKGS := $(or $(PKG_FILTER),$(PACKAGES))

# Convert hyphenated package name to Python import name (e.g. pytrade-backtest -> pytradebacktest)
pkg_to_import = $(subst -,,$(1))

# Computed paths used by sub-makefiles
SRC_DIRS  := $(foreach pkg,$(SELECTED_PKGS),$(SRC_DIR)/$(pkg)/$(call pkg_to_import,$(pkg)))
LINT_DIRS := $(SRC_DIRS) tests
COV_ARGS  := $(foreach pkg,$(SELECTED_PKGS),--cov=$(call pkg_to_import,$(pkg)))
MYPY_ARGS := $(foreach pkg,$(SELECTED_PKGS),-p $(call pkg_to_import,$(pkg)))

# Allow package names as make goals (no-op targets)
ifneq ($(PKG_FILTER),)
$(PKG_FILTER): @:
endif

.DEFAULT_GOAL := help

.EXPORT_ALL_VARIABLES:

include makefiles/development.mk
include makefiles/help.mk
include makefiles/lint.mk
include makefiles/local.mk
include makefiles/test.mk

.PHONY: list-packages
list-packages: ##@other List all packages in src/
	@echo "Available packages:"
	@for pkg in $(PACKAGES); do echo "  - $$pkg"; done
	@echo ""
	@echo "Usage: make <target> [package]"
