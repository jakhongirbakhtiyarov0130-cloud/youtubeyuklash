# Python 3.11 image dan foydalanamiz
FROM python:3.11-slim

# FFmpeg o'rnatish (YouTube yuklamalari uchun shart)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Ishchi katalogni belgilaymiz
WORKDIR /app

# Kutubxonalarni o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chiramiz
COPY . .

# Botni ishga tushiramiz
CMD ["python", "main.py"]
