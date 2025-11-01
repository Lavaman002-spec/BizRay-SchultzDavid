# =========================
# BizRay Frontend Dockerfile (Next.js 15.5.5 with Turbopack)
# =========================
FROM node:20-alpine AS builder

# 1️⃣ Setup working directory
WORKDIR /app

# 2️⃣ Copy dependency files
COPY package.json package-lock.json* ./

# 3️⃣ Install deps
RUN npm install

# 4️⃣ Copy all source files
COPY . .

# 5️⃣ Build the production bundle (Turbopack)
RUN NEXT_DISABLE_ESLINT=1 npm run build

# 6️⃣ Expose app port
EXPOSE 3000

# 7️⃣ Start Next.js in production mode
CMD ["npm", "run", "start"]
