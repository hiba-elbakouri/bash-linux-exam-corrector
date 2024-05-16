correction: ## build and run correction container
	docker build --build-arg EXAM_TYPE=$(EXAM_TYPE) --build-arg EXAM_FOLDER=$(EXAM_FOLDER) -t exam_corrector .
	docker run --rm exam_corrector

