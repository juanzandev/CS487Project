# 🎓 Canvas Grade Widget - Setup Guide

Welcome! This guide will help you set up the Canvas Grade Widget on your Windows computer.

## 📋 What You Need

✅ **Windows 10 or 11** (64-bit)  
✅ **Canvas LMS account** (school provided)  
✅ **Internet connection**  
✅ **5 minutes of setup time**

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your Canvas API Token

1. **Log into your Canvas account** (your school's website)
2. Click on **Account** (top-left corner) → **Settings**
3. Scroll down to **"Approved Integrations"**
4. Click **"+ New Access Token"**
5. **Purpose:** Enter "Grade Widget" or any description
6. Click **Generate Token**
7. **COPY THE TOKEN IMMEDIATELY** ⚠️ You won't see it again!

### Step 2: Configure the App

1. **Right-click** on `config.example.py` → **"Open with"** → **Notepad**
2. **Replace the template values** with your information:

```python
# Canvas API Configuration
CANVAS_BASE_URL = "https://your-school.instructure.com"  # ← Your school's Canvas URL
API_TOKEN = "paste_your_token_here"                       # ← Your API token from Step 1
THEME = "auto"  # Options: "auto", "light", "dark", "nord"
```

3. **Save the file as:** `config.py` (remove ".example")
   - In Notepad: **File** → **Save As** → Change name to `config.py`

### Step 3: Run the App

1. **Double-click** `CanvasGradeWidget_Fixed.exe`
2. If Windows shows a security warning:
   - Click **"More info"** → **"Run anyway"**
   - This is normal for new applications

🎉 **Done!** Your grades should appear in a beautiful desktop widget!

## 🎨 Features You'll See

- **Your Profile:** Circular profile picture and name from Canvas
- **Live Grades:** Real-time grade updates from all your courses
- **Beautiful Themes:** Auto-switching between light/dark modes
- **Elegant Design:** Gradient backgrounds and smooth animations

## 🔧 Troubleshooting

### "The application failed to start"

- Make sure you're using the `config.py` file (not `config.example.py`)
- Check that your Canvas URL is correct (usually ends with `.instructure.com`)

### "No courses found" or connection errors

- Verify your API token is correct and not expired
- Make sure your Canvas URL is exactly as it appears in your browser
- Check your internet connection

### Windows Security Warning

- This is normal! The app is safe but not digitally signed
- Click **"More info"** then **"Run anyway"**

### Grades not updating

- Click the refresh button (🔄) in the widget
- Check if your Canvas account has access to grades

## 🔒 Security & Privacy

✅ **Your data stays local** - No information is sent to third parties  
✅ **API token is secure** - Only stored in your config.py file  
✅ **Open source** - You can review the code if desired  
✅ **No password storage** - Uses Canvas API tokens only

## ⚙️ Customization

### Change Theme

- Right-click the widget → Settings → Select theme → Save
- **Auto:** Follows your Windows theme
- **Light:** Clean, bright interface
- **Dark:** Easy on the eyes
- **Nord:** Developer-inspired color scheme

### Move the Widget

- Simply **drag** the widget anywhere on your screen
- Position stays saved between app restarts

## 🆘 Need Help?

**Common Canvas URLs:**

- `https://[school-name].instructure.com`
- `https://canvas.[school-name].edu`
- `https://[school-name].learn.canvas.net`

**Still need help?** Contact your IT department or the app developer.

---

## 📱 About This App

**Canvas Grade Widget** is a free, open-source desktop application that helps students monitor their academic performance in real-time. Built with modern technologies for a beautiful, responsive experience.

**Version:** 2.0  
**Compatible with:** Canvas LMS  
**Requires:** Internet connection for grade updates

---

_Enjoy tracking your academic success! 🎓_
