# 🚀 Deployment Guide: Next-Gen Converter

Your application is now **Production Ready**. It is equipped with:
-   **Smart PDF Engine** (LibreOffice + Python Fallback + Check logic).
-   **Smart OCR** (Tesseract for Scans).
-   **High-Fidelity Audio** (FFmpeg 320kbps).
-   **Universal Limits** (50MB/100MB/200MB safe limits).

## Option 1: Render.com (Recommended / Easiest)
Render works great with `Docker` and offers a free tier.

1.  **Push your code to GitHub**.
2.  **Create New Web Service** on Render.
3.  **Connect GitHub Repo**.
4.  **Select "Docker"** as the Environment.
    -   Render will find the `Dockerfile` automatically.
5.  **Deploy**.
    -   *Note*: Render's free tier is slow to build (Docker takes time). Be patient (5-10 mins).

## Option 2: Railway.app (Faster / Robust)
Railway usually builds Docker images much faster. The process is identical: "New Project -> Deploy from GitHubRepo".

## Option 3: Local Windows (For You)
You are already running it!
-   To ensure 100% "Pro" features locally:
    -   Install [LibreOffice](https://www.libreoffice.org/).
    -   Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
    -   The app will auto-detect them on restart.

## 🛠️ Environment Variables
You don't need many, but if you want to change limits or ports:
-   `PORT`: Defaults to 5000.
-   `MAX_CONTENT_LENGTH`: Defaults to 500MB (backend limit).

## ✅ Final Checklist
-   [x] `Dockerfile` created (includes LibreOffice, FFmpeg, Tesseract).
-   [x] `requirements.txt` updated.
-   [x] Codebase Refactored for Quality.

**Congratulations! Your Universal Analyzer/Converter is ready.**
