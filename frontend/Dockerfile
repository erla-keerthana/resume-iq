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

# Run as non-root user
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV PORT=5174
ENV BACKEND_URL=http://backend:8001
ENV ORIGIN=http://localhost:5174
EXPOSE ${PORT}

CMD ["node", "build"]
