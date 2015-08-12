run:	build
	@docker run \
		--rm \
		-ti \
		-p 5000:5000 \
		-v /home/dragon/git/mot/app/static:/dockermount:ro \
		data


build:
	@docker build -t data .

.PHONY: run build
