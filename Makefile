.PHONY: style lint test profile

lint:
	python3 -m pylint -rn qiskit_qcgpu_provider 

style:
	python3 -m pycodestyle --max-line-length=120 qiskit_qcgpu_provider tests

test:
	python3 -m unittest tests