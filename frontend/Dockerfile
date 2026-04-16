FROM node:20-alpine

WORKDIR /workspace/frontend

COPY frontend/package.json /workspace/frontend/package.json
COPY frontend/tsconfig.json /workspace/frontend/tsconfig.json
COPY frontend/tsconfig.app.json /workspace/frontend/tsconfig.app.json
COPY frontend/tsconfig.node.json /workspace/frontend/tsconfig.node.json
COPY frontend/vite.config.ts /workspace/frontend/vite.config.ts
COPY frontend/postcss.config.js /workspace/frontend/postcss.config.js
COPY frontend/tailwind.config.js /workspace/frontend/tailwind.config.js
COPY frontend/index.html /workspace/frontend/index.html
COPY frontend/src /workspace/frontend/src

RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

