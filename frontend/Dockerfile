FROM node:20-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-slim

WORKDIR /app

COPY --from=build /app/build ./build
COPY --from=build /app/package.json .
COPY --from=build /app/node_modules ./node_modules

ENV PORT=5174
ENV BACKEND_URL=http://backend:8001
ENV ORIGIN=http://10.10.0.36:5174
EXPOSE ${PORT}

CMD ["node", "build"]
