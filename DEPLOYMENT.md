# 🚀 ShobKaj Deployment Guide

This guide will help you deploy ShobKaj to **Railway.app** (free tier).

---

## Prerequisites

1. **Git** - [Download Git](https://git-scm.com/download/win)
2. **GitHub Account** - [Sign up](https://github.com/signup)
3. **Railway Account** - [Sign up with GitHub](https://railway.app/)

---

## Step 1: Install Git

1. Download Git from: https://git-scm.com/download/win
2. Run the installer (use default settings)
3. Restart your terminal/VS Code

---

## Step 2: Push to GitHub

Open terminal in the project folder and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: ShobKaj marketplace"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/shobkaj.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy to Railway

### Option A: Via Website (Easiest)

1. Go to [railway.app](https://railway.app/) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `shobkaj` repository
5. Railway will auto-detect the Dockerfile and start building

### Add PostgreSQL Database:

1. In your Railway project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway will automatically set the `DATABASE_URL` environment variable

### Set Environment Variables:

Click on your service → **Variables** tab → Add:
```
SPRING_PROFILES_ACTIVE=prod
```

### Get Your URL:

1. Go to **Settings** tab
2. Under **Domains**, click **"Generate Domain"**
3. Your app will be live at: `https://shobkaj-xxxx.railway.app`

---

## Step 4: Verify Deployment

Visit your Railway URL and you should see the ShobKaj homepage!

Test the API:
```
https://your-app.railway.app/api/workers
```

---

## Troubleshooting

### Build Fails
- Check the deploy logs in Railway dashboard
- Ensure all files are committed to git

### Database Connection Error
- Make sure PostgreSQL addon is added
- Check that `DATABASE_URL` variable exists

### App Crashes on Start
- Check logs: Railway Dashboard → Deployments → View Logs
- Ensure `SPRING_PROFILES_ACTIVE=prod` is set

---

## Local Development

For local development, the app still uses H2 in-memory database:

```bash
# Run locally (uses H2 database)
./mvnw spring-boot:run

# Or with production profile (needs PostgreSQL locally)
./mvnw spring-boot:run -Dspring-boot.run.profiles=prod
```

---

## Project Structure

```
shobkaj.com/
├── src/main/resources/
│   ├── application.properties      # Local/Dev config (H2)
│   └── application-prod.properties # Production config (PostgreSQL)
├── Dockerfile                       # Docker build instructions
├── railway.json                     # Railway configuration
└── .gitignore                       # Git ignore patterns
```

---

## Estimated Costs

| Service | Free Tier |
|---------|-----------|
| Railway | $5/month credit (enough for hobby projects) |
| PostgreSQL | Included with Railway |

---

**Need help?** Check Railway docs: https://docs.railway.app/

🎉 **Congratulations! Your ShobKaj app is now live on the internet!**
