# 🚀 Deploy DebriSense to Render

## Prerequisites
- GitHub account with your DebriSense repository
- Render account (free tier available)

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 1.2 Verify Files
Ensure these files are in your repository:
- ✅ `app.py` (Flask application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `render.yaml` (Render configuration)
- ✅ `.gitignore` (Git ignore rules)
- ✅ `index.html` (Login page)
- ✅ `dashboard.html` (Main dashboard)
- ✅ `enhanced_styles.css` (Styles)
- ✅ `enhanced_script.js` (JavaScript)
- ✅ `data/data.csv` (River data)
- ✅ `data/image/` (Images folder)

## Step 2: Deploy on Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Verify your email

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your DebriSense repository

### 2.3 Configure Service
- **Name:** `debrisense-dashboard`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Plan:** Free (or choose paid for more resources)

### 2.4 Environment Variables
Add these environment variables in Render dashboard:
- **Key:** `WEATHER_API_KEY`
- **Value:** Your WeatherAPI.com key (optional)
- **Sync:** No

### 2.5 Deploy
1. Click **"Create Web Service"**
2. Wait for build to complete (2-5 minutes)
3. Your app will be available at: `https://your-app-name.onrender.com`

## Step 3: Verify Deployment

### 3.1 Test Login Page
- Visit your Render URL
- Should see the DebriSense login page
- Use credentials: `user@pinc.my` / `123456`

### 3.2 Test Dashboard
- Login should redirect to dashboard
- Check if map loads correctly
- Verify sensor data and weather integration

### 3.3 Test API Endpoints
- `/get_all_locations` - Should return river data
- `/get_sensor_data/Sungai Inanam` - Should return sensor data
- `/get_weather_data/Sungai Inanam` - Should return weather data

## Step 4: Custom Domain (Optional)

### 4.1 Add Custom Domain
1. Go to your service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Update DNS records as instructed

## Troubleshooting

### Common Issues

**Build Fails:**
- Check `requirements.txt` syntax
- Verify all dependencies are listed
- Check Python version compatibility

**App Won't Start:**
- Verify `gunicorn` is in requirements.txt
- Check start command syntax
- Review build logs for errors

**Images Not Loading:**
- Ensure `data/image/` folder is in repository
- Check file permissions
- Verify image paths in CSV

**Weather API Issues:**
- Set `WEATHER_API_KEY` environment variable
- Check API key validity
- Review weather system logs

### Debug Commands
```bash
# Check build logs
# View in Render dashboard

# Test locally with production settings
export PORT=5000
export FLASK_ENV=production
python app.py
```

## Performance Optimization

### Free Tier Limitations
- **Sleep after 15 minutes** of inactivity
- **512 MB RAM** limit
- **Shared CPU** resources

### Optimization Tips
- Enable **Auto-Deploy** for updates
- Use **Health Checks** for monitoring
- Consider **Paid Plan** for production use

## Monitoring

### Health Check URL
- Add: `https://your-app.onrender.com/`
- Expected: 200 OK response

### Logs
- View real-time logs in Render dashboard
- Monitor for errors and performance issues

## Security Notes

### Environment Variables
- Never commit API keys to repository
- Use Render's environment variable system
- Rotate keys regularly

### HTTPS
- Render provides free SSL certificates
- All traffic is automatically encrypted

## Support

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Python Deployment Guide](https://render.com/docs/deploy-python-app)

### DebriSense Issues
- Check GitHub repository issues
- Review application logs
- Test locally first

---

**🎉 Congratulations!** Your DebriSense application is now live on Render!
