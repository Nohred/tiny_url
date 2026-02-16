FROM node:20-alpine

WORKDIR /frontend

COPY package.json package-lock.json* /frontend/
RUN npm install

COPY . /frontend

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
