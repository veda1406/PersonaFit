.PHONY: setup pipeline test app clean

setup:
	pip install -r requirements.txt

pipeline:
	python run_pipeline.py

test:
	pytest tests/ -v --tb=short

app:
	streamlit run app/streamlit_app.py --server.port 8501

mlflow-ui:
	mlflow ui --port 5000

docker-build:
	docker build -t personafit .

docker-run:
	docker run -p 8501:8501 personafit

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

all: setup pipeline test app
