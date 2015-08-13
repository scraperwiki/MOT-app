run:	build
	@docker run \
		--rm \
		-ti \
		-p 5000:5000 \
		-v "/dockermount:/dockermount:ro" \
		data


build:
	@docker build -t data .

.PHONY: run build
