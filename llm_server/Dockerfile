FROM python:3.12

# Install ffmpeg for pydub + audio conversion
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# Copy requirements (adjust if yours differ)
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade openai
RUN pip install --no-cache-dir -r requirements.txt


# Copy your server code into the container (adjust as needed)
COPY server.py server.py

# Expose port for websockets
EXPOSE 8080

# Start your server
CMD ["python", "server.py"]