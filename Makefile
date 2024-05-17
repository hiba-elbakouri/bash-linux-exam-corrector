.EXPORT_ALL_VARIABLES:

# Define the default target
.DEFAULT_GOAL := run_correction

# Define variables
EXAM_FOLDER ?=

.PHONY: build_correction run_correction

SHELL := /bin/bash

# Rule to build the correction container
build_correction:
	@if [ "$(EXAM_TYPE)" = "docker" ]; then \
		docker build -t my-dind-image -f Dockerfile_DIND . ;\
	else \
		docker build --build-arg EXAM_TYPE=$(EXAM_TYPE) --build-arg EXAM_FOLDER=$(EXAM_FOLDER) -t exam_corrector . ;\
	fi

# Rule to run the correction container
run_correction: build_correction
	@if [ "$(EXAM_TYPE)" = "docker" ]; then \
		docker run -v /var/run/docker.sock:/var/run/docker.sock -it my-dind-image ;\
	else \
		docker run --rm exam_corrector ;\
	fi
