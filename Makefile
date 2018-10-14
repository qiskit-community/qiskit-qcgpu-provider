.PHONY: style lint test profile

lint:
	python3 -m pylint -rn qiskit_qcgpu_provider 

style:
	python3 -m pycodestyle --max-line-length=100 qiskit_qcgpu_provider test

test:
	python3 -m unittest discover -v

profile:
	python3 -m unittest discover -p "profile*.py" -v
