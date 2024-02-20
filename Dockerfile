# Verwenden Sie ein offizielles Python-Image als Basis
FROM python:3.10-slim

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# Kopieren der benötigten Dateien in den Container
COPY requirements.txt .
COPY . .

# Installieren Sie Chrome
RUN apt-get update && apt-get install -y wget gnupg2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Bereinigen Sie unnötige Pakete und Dateien, um die Größe des Images zu reduzieren
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Installieren Sie Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Setzen der Umgebungsvariablen für den Headless-Modus
ENV DISPLAY=:99

# Startkommando
CMD ["python","-u","main.py"]
