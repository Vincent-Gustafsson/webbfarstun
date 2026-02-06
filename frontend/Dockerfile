# Use Node.js LTS (Long Term Support)
FROM node:lts-alpine

WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the Vite port
EXPOSE 5173

# Run the dev server
CMD ["npm", "run", "dev", "--", "--host"]
