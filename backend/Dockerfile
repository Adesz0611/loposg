# Python alap image
FROM python:3.9

# Mappa létrehozása a kódfájlok számára
WORKDIR /app

# Függőségek telepítése
COPY requirements.txt .
RUN pip install -r requirements.txt

# Backend indítása Quart szerverrel
CMD ["quart", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
