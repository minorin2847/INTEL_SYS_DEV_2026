# Static build of the React client, served by nginx which also reverse-proxies
# /api/* to the api container (see nginx.conf). Build context is web/.
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build          # VITE_API_BASE unset -> the app calls "/api" (nginx proxies it)

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
