FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# Dev server bound to 0.0.0.0 so it is reachable from the host
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
