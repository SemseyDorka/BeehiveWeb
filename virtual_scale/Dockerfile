FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir requests
COPY sim.py .
CMD ["python", "-u", "sim.py"]