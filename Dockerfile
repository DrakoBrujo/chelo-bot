FROM python:3.9-buster

# Instalar ffmpeg y otras dependencias necesarias
RUN apt-get update && apt-get install -y ffmpeg

# Copiar el código de la aplicación
COPY . .

# Instalar dependencias
RUN pip install -r requirements.txt

# Comando para ejecutar tu bot
CMD ["python", "main.py"]
