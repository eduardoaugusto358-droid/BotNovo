FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Create sessions directory
RUN mkdir -p sessions

EXPOSE 3001

CMD ["npm", "start"]