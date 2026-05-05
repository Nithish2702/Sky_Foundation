# Qatar Foundation Admin Portal - Frontend

This is the frontend for the Qatar Foundation Admin Portal.

## 🚀 Deployment on Render

### Quick Deploy
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Static Site"
3. Connect your repository
4. Configure:
   - **Root Directory**: `Test1/sky`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`
5. Click "Create Static Site"

### After Deployment
Update your backend environment variable:
- Add `FRONTEND_URL` with your frontend URL
- Example: `https://qatar-foundation-frontend.onrender.com`

## 📁 Files Structure
```
sky/
├── admin.html          # Main HTML file
├── admin.css           # Styles
├── admin.js            # Frontend logic
├── api.js              # API integration
├── _redirects          # Render routing config
├── render.yaml         # Render configuration
└── README.md           # This file
```

## 🔗 Backend Connection
The frontend automatically connects to:
- **Local**: `http://localhost:5000/api`
- **Production**: `https://sky-foundation.onrender.com/api`

## 🛠️ Local Development
1. Start backend: `cd ../backend && python app.py`
2. Start frontend server: `python -m http.server 8000`
3. Open: `http://localhost:8000/admin.html`

## 📝 Environment Detection
The app automatically detects if it's running locally or in production and uses the appropriate API URL.
