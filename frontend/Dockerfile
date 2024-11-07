# Alap image a Node.js számára
FROM node:18 as build

# Mappa létrehozása a kódfájlok számára
WORKDIR /app

# Csomagfájlok másolása és telepítése
ARG NODE_ENV
ENV NODE_ENV=$NODE_ENV
COPY package*.json ./
RUN npm install --verbose

# A teljes kód másolása a konténerbe
COPY . .

# Alkalmazás futtatása a beépített szerveren
CMD ["npm", "run", "dev"]
