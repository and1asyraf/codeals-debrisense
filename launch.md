# 🚀 Launch Instructions - Debrisense AI Dashboard

## Quick Start (2 Steps)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Everything
```bash
python app.py
```
*That's it! Everything runs from one server* 🎉

### 3. Access Dashboard
- Open your browser
- Go to: **http://localhost:5000**
- Enjoy your AI-powered dashboard! 🚀

## What You'll See
- **Map**: Dark theme map focused on Malaysia
- **Markers**: Click the donut-shaped markers on rivers
- **AI Insights**: Sidebar shows predictions and warnings
- **Real-time Analysis**: AI analyzes environmental data

## Troubleshooting
- **If markers don't work**: Make sure `python app.py` is running
- **If images don't show**: Check that `data/image/` folder has the PNG files
- **If predictions fail**: The dashboard will show basic info as fallback

## Files Structure
```
Debrisense-Proto2/
├── dashboard.html      ← Open this in browser
├── app.py             ← Run this for AI backend
├── requirements.txt   ← Python packages
├── data/
│   ├── data.csv       ← Location data
│   └── image/         ← River images
└── models/            ← AI models (auto-created)
```

**That's all you need!** 🎯
