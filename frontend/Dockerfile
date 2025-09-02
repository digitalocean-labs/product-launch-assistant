FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (need dev dependencies for build)
RUN npm ci

# Copy frontend source
COPY . ./

# Build argument for API URL (available during build)
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Build the React app (environment variables baked in here)
RUN npm run build
# Add build timestamp to force fresh deployments
RUN echo "Build timestamp: $(date)" > build/build-info.txt

# Install serve to serve the built app
RUN npm install -g serve

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 --ingroup nodejs nextjs

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the built React app
# Serve the built React app with no caching to ensure fresh content
# -c 0 disables caching, -n disables etag, -s serves SPA
CMD ["serve", "-s", "build", "-l", "3000", "-c", "0", "-n"]