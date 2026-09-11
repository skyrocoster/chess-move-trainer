FROM node:24-bookworm-slim

ENV NPM_CONFIG_UPDATE_NOTIFIER=false

WORKDIR /workspace

COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/package.json
COPY experiments/package.json ./experiments/package.json
RUN npm ci --workspace frontend --include-workspace-root=false \
    && sha256sum package-lock.json > ./frontend/node_modules/.package-lock.sha256 \
    && mkdir -p /opt/frontend-node-modules \
    && cp -a ./frontend/node_modules/. /opt/frontend-node-modules/

COPY frontend ./frontend
COPY frontend/docker-entrypoint.sh /usr/local/bin/chess-move-trainer-frontend-entrypoint
RUN chmod +x /usr/local/bin/chess-move-trainer-frontend-entrypoint

ENTRYPOINT ["chess-move-trainer-frontend-entrypoint"]
CMD ["npm", "--workspace", "frontend", "run", "dev", "--", "--host", "0.0.0.0"]
