# Use an official Node.js image
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package.json and lock file
COPY package.json ./

# Install dependencies
RUN yarn install

# Copy the rest of the source
COPY . .

# Build the React app
RUN yarn build

# Use an Nginx container for serving the production build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
