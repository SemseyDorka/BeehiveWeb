FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir requests
COPY sim.py .
CMD ["python", "-u", "sim.py"]