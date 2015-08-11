all: generated/mot.json \

generated/mot.json: build generate.py mot-user-data.yml
	@mkdir -p generated
	@docker run \
		--volume $$PWD/generate.py:/code/generate.py \
		--volume $$PWD/mot-user-data.yml:/code/mot-user-data.yml \
	        --rm \
		mot-pypy > generated/mot.json
	@echo Built generated/\*.json

build: .FORCE
	@docker build -t mot-pypy .

.PHONY: all .FORCE
.FORCE:
