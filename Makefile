.ONESHELL:
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
_SPACE = $(eval) $(eval)
_COMMA := ,

#####
# VARS
#####

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MKFILE_DIR := $(patsubst %/,%,$(dir $(MKFILE_PATH)))

VENV_DIR := .venv

# add venv bin to PATH
export PATH := $(MKFILE_DIR)/$(VENV_DIR)/bin:$(PATH)

TESTS_TARGETS :=

# Files who need to be updated when build target is asked
BUILD_FILES := pyproject.toml
# Files who need to be updated when release target is asked
RELEASE_FILES := CHANGELOG.md .VERSION $(BUILD_FILES)
# GHA Workflows templates
GHA_TEMPLATES_DIR := .github/workflows
GHA_TEMPLATES_SRC := $(wildcard $(GHA_TEMPLATES_DIR)/*.j2)
GHA_TEMPLATES_INC := $(wildcard $(GHA_TEMPLATES_DIR)/*.inc)
GHA_TEMPLATES := $(GHA_TEMPLATES_SRC:%.j2=%)

#####
# Versions
#####

GIT_CHANGELOG_VERSION := 0.2.1
PYTHON_VERSIONS := $(shell cat .python-version | sed -e 's/.[0-9]\+$$//g')
BASE_PYTHON_VERSION := $(firstword $(PYTHON_VERSIONS))

#####
# Function
#####

define check_cmd_path
  $(eval
  _EXECUTABLE = $(1)
  _EXPECTED_PATH = $(2)
  _MSG = $(3)
  ifndef _EXECUTABLE
    $$(error Missing argument on 'check_cmd' call)
  endif
  $$(info Checking presence of '$$(_EXECUTABLE)')
  _CMD_PATH = $$(shell PATH="$$(PATH)" which $$(_EXECUTABLE))
  ifneq ($$(_CMD_PATH),)
    ifdef _EXPECTED_PATH
      ifneq ($$(_CMD_PATH),$$(_EXPECTED_PATH))
        ifneq ($$(_MSG),)
          $$(error $$(_MSG))
        endif
        ifeq ($$(_CMD_PATH),)
          $$(error Expecting '$$(_EXECUTABLE)' to be in '$$(_EXPECTED_PATH)' but is not installed)
        else
          $$(error Expecting '$$(_EXECUTABLE)' to be in '$$(_EXPECTED_PATH)' but found in '$$(_CMD_PATH)')
        endif
      endif
    endif
  else
    $$(error '$$(_EXECUTABLE)' not found in $$$$PATH)
  endif
  $$(info OK '$$(_EXECUTABLE)' found in '$$(_CMD_PATH)'...)
  )
endef

#####
# Include
#####

-include $(VENV_DIR)/tox-env.mk

#####
# Targets
#####

# invoking make V=1 will print everything
.PHONY: $(V).SILENT
$(V).SILENT:

.PHONY: all
all: test build

.PHONY: .FORCE
.FORCE:

$(VENV_DIR)/tox-env.mk: tox.ini | venv
	$(info ### Generating targets based on tox environments... ###)
	$(call check_cmd_path,tox,$(MKFILE_DIR)/$(VENV_DIR)/bin/tox)
	TEST_TOX_ENV_LIST=$$($(VENV_DIR)/bin/tox -q -l 2> /dev/null | tr '\n' ' ')
	cat << EOF > $(@)
		TEST_TOX_TARGETS_PREFIX := test-tox
		TEST_TOX_ENV_LIST := $${TEST_TOX_ENV_LIST}
		TEST_TOX_TARGETS := \$$(addprefix \$$(TEST_TOX_TARGETS_PREFIX)-,\$$(TEST_TOX_ENV_LIST))
		TESTS_TARGETS := \$$(TESTS_TARGETS) \$$(TEST_TOX_TARGETS)
	EOF

.PHONY: test
test: $(TESTS_TARGETS) docs build

.PHONY: $(TEST_TOX_TARGETS)
$(TEST_TOX_TARGETS): TOX_ENV = $(subst $(TEST_TOX_TARGETS_PREFIX)-,,$(@))
$(TEST_TOX_TARGETS): venv pyproject.toml github-workflows
	tox -e $(TOX_ENV)

##############
# Python env #
##############

.PHONY: venv
venv: $(VENV_DIR)/bin/activate .python-venv

.SECONDARY: $(VENV_DIR)/bin/activate
$(VENV_DIR)/bin/activate: dev-requirements.txt .python-version
	$(info ### Generating Python env ###)
	$(call check_cmd_path,python$(BASE_PYTHON_VERSION))
	$(call check_cmd_path,pip3)
	pip$(BASE_PYTHON_VERSION) install --quiet --quiet virtualenv
ifdef VIRTUAL_ENV
ifneq ($(VIRTUAL_ENV),$(VENV_DIR))
	$(error VIRTUAL_ENV '$(VIRTUAL_ENV)' already set.$(VENV_DIR) Quit this VIRTUAL_ENV before running tests)
endif
endif
	$(info Installing $(BASE_PYTHON_VERSION) tests requirements)
	virtualenv --quiet -p $(shell command -v python$(BASE_PYTHON_VERSION)) $(@D)/../
	VIRTUAL_ENV_DISABLE_PROMPT=true . $@
	pip install --quiet --quiet -Ur $<
	touch $@

.python-venv: $(VENV_DIR)/bin/activate
	$(info ### Generating venv link $(@) ###)
	ln -sfr $(VENV_DIR)/bin/activate $(@)

###################
# Github workflows
###################
.PHONY: github-workflows
github-workflows: $(GHA_TEMPLATES)

#######
# Release
#######

.PHONY: release
release:
	# Check that the repository is clean
	$(MAKE) --no-print-directory check-git-clean
	# Update $(RELEASE_FILES)
	# commit changes
	# add a tag if needed
	CURRENT_GIT_BRANCH=$$(git rev-parse --abbrev-ref HEAD)
	export LAST_TAG=$$(git for-each-ref --merged $$CURRENT_GIT_BRANCH --sort=-creatordate --format '%(refname)' refs/tags | sed 's/refs\/tags\///' | head -n1)
	export NEXT_TAG=$$(docker run --rm -v $$PWD:/tmp --workdir /tmp ghcr.io/caarlos0/svu next --strip-prefix)
	# Only if we have both information
	if [[ -z "$${LAST_TAG:-}" || -z "$${NEXT_TAG:-}" ]];then
		1>&2 echo "Release asked but missing LAST_TAG or NEXT_TAG"
		exit 1
	fi
	if [[ "$${LAST_TAG:-}" == "$${NEXT_TAG:-}" ]];then
		1>&2 echo "Release asked but LAST_TAG and NEXT_TAG are equal"
		exit 1
	fi
	# Check if the future tag already exists
	if git show-ref --tags "$${NEXT_TAG:-}" --quiet &> /dev/null; then
		1>&2 echo "Tag '$${NEXT_TAG:-}' already exists"
		exit 1
	else
		true
	fi
	# Update files used in release
	$(MAKE) --no-print-directory $(RELEASE_FILES)
	# Check that the build still working
	$(MAKE) --no-print-directory build
	if ! git ls-files --error-unmatch $(RELEASE_FILES) > /dev/null 2>&1 || ! git diff --exit-code $(RELEASE_FILES) > /dev/null 2>&1;then
		printf '%s\n' "##### Commit changes #####"
		git add $(RELEASE_FILES)
		git commit -m"Release $${NEXT_TAG:-} [skip ci]"
		$(MAKE) --no-print-directory tag
	fi
	# Check that the repository is clean
	$(MAKE) --no-print-directory check-git-clean

.PHONY: release-gh
release-gh:
	CURRENT_TAG=$$(git tag --points-at)
	if [[ "$${CURRENT_TAG:-}" ]];then
		echo "Create GH release '$${CURRENT_TAG:-}'"
		CHANGELOG=$$(docker run --rm -e CHANGELOG_TAG="$${CURRENT_TAG:-}" -v $$PWD:/git rockandska/git-changelog:$(GIT_CHANGELOG_VERSION) -p)
		gh release create "$${CURRENT_TAG}" -t "$${CURRENT_TAG:-}" --notes "$${CHANGELOG}"
	else
		1>&2 echo "No tag present"
		1>&2 echo "Abort"
		exit 1
	fi


CHANGELOG.md: .FORCE
	if [[ -z "$${NEXT_TAG:-}" ]];then
		printf '%s\n' "##### Update $@ (version: 'Unreleased' ) #####"
		docker run --rm -e CHANGELOG_TAG="$${NEXT_TAG:-}" -v $$PWD:/git rockandska/git-changelog:$(GIT_CHANGELOG_VERSION)
		if ! git ls-files --error-unmatch $@ > /dev/null 2>&1 || ! git diff --exit-code $@ > /dev/null 2>&1;then
			printf '%s\n' "##### Commit changes #####"
			git add $@
			git commit -q -m "Changelog update [skip ci]"
		fi
	else
		printf '%s\n' "##### Update $@ (version: '$$NEXT_TAG' ) #####"
		docker run --rm -e CHANGELOG_TAG="$${NEXT_TAG:-}" -v $$PWD:/git rockandska/git-changelog:$(GIT_CHANGELOG_VERSION)
	fi

.PHONY: tag
.SECONDARY: tag
tag: check-git-clean
	if [[ -n "$${NEXT_TAG:-}" ]];then
		printf '%s\n' "##### Add tag '$$NEXT_TAG' #####"
		git tag -m "$${NEXT_TAG}" "$${NEXT_TAG}"
	fi

.SECONDARY: .VERSION
.VERSION: .FORCE
	if [[ -n "$${NEXT_TAG:-}" ]];then
		echo "$${NEXT_TAG}" > $@
		printf '%s\n' "##### $@ updated with '$${NEXT_TAG}' #####"
	fi

.PHONY: build
build:
	printf '%s\n' "##### Build #####"
	$(VENV_DIR)/bin/poetry lock --check
	$(VENV_DIR)/bin/poetry build

.PHONY: publish
publish: build
	CURRENT_TAG=$$(git tag --points-at)
	if [[ "$${CURRENT_TAG:-}" ]];then
		echo "Publishing release '$${CURRENT_TAG:-}'"
		$(VENV_DIR)/bin/poetry publish
	else
		1>&2 echo "No tag present"
		1>&2 echo "Abort"
		exit 1
	fi

.PHONY: check-git-clean
.SECONDARY: check-git-clean
check-git-clean:
	if ! output=$$(git status --porcelain 2>&1) || [ -n "$${output}" ];then
		1>&2 echo "Git workingtree is not clean"
		exit 1
	fi

.PHONY: docs-serve
docs-serve: pyproject.toml
	$(VENV_DIR)/bin/poetry lock --check
	$(VENV_DIR)/bin/poetry install --only docs
	$(VENV_DIR)/bin/poetry run mkdocs serve

.PHONY: docs
docs: pyproject.toml
	$(VENV_DIR)/bin/poetry lock --check
	$(VENV_DIR)/bin/poetry install --only docs
	$(VENV_DIR)/bin/poetry run mkdocs build


##############
# Templates
##############

tox.ini: tox.ini.j2 | venv
	$(info ### Generating $@ from $<... ###)
	jinja2 -o $@ $< -D base_python_version="$(BASE_PYTHON_VERSION)" -D python_versions="$(PYTHON_VERSIONS)"

pyproject.toml: pyproject.toml.j2 .FORCE | venv
	$(info ### Generating $@ from $<... ###)
	CURRENT_VERSION=$$(<".VERSION")
	jinja2 -o $@ $< -D version="$$CURRENT_VERSION" -D python_versions="$(PYTHON_VERSIONS)"

$(GHA_TEMPLATES): %.yml: %.yml.j2 $(GHA_TEMPLATES_INC) tox.ini.j2 .FORCE | venv
	$(info ### Generating $@ from $<... ###)
	mkdir -p $(@D)
	jinja2 -o $@ $< -D tox_targets="$(TEST_TOX_TARGETS)" -D tox_targets_prefix="$(TEST_TOX_TARGETS_PREFIX)" -D base_python_version="$(BASE_PYTHON_VERSION)"
