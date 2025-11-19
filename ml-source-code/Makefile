# Makefile for ML Monorepo

.PHONY: help build-all build-component push-component test clean

# Components
COMPONENTS := data_ingestion data_processing data_eda train inference

# AWS config
AWS_CONFIG := config/aws.json
ECR_REGISTRY := 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com
AWS_REGION := ap-southeast-2

help:
	@echo "Available commands:"
	@echo "  make build-component COMPONENT=<name>  - Build Docker image for a component"
	@echo "  make build-all                        - Build all component images"
	@echo "  make push-component COMPONENT=<name>   - Push component image to ECR"
	@echo "  make test                             - Run tests (placeholder)"

build-component:
	@if [ -z "$(COMPONENT)" ]; then \
		echo "Error: COMPONENT is required. Usage: make build-component COMPONENT=data_ingestion"; \
		exit 1; \
	fi
	@echo "Building $(COMPONENT)..."
	docker build -t $(COMPONENT):local -f components/$(COMPONENT)/Dockerfile components/$(COMPONENT)/

build-all:
	@for component in $(COMPONENTS); do \
		echo "Building $$component..."; \
		docker build -t $$component:local -f components/$$component/Dockerfile components/$$component/ || exit 1; \
	done
	@echo "All components built successfully!"

push-component:
	@if [ -z "$(COMPONENT)" ]; then \
		echo "Error: COMPONENT is required. Usage: make push-component COMPONENT=data_ingestion TAG=latest"; \
		exit 1; \
	fi
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required. Usage: make push-component COMPONENT=data_ingestion TAG=latest"; \
		exit 1; \
	fi
	@echo "Pushing $(COMPONENT):$(TAG) to ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker tag $(COMPONENT):local $(ECR_REGISTRY)/$(COMPONENT):$(TAG)
	docker push $(ECR_REGISTRY)/$(COMPONENT):$(TAG)
	@echo "Successfully pushed $(ECR_REGISTRY)/$(COMPONENT):$(TAG)"

test:
	@echo "Running tests... (placeholder)"
	@for component in $(COMPONENTS); do \
		echo "Testing $$component..."; \
	done

clean:
	@echo "Cleaning up..."
	docker system prune -f

