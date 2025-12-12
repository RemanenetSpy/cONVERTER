# Google Analytics Setup Guide

## Step 1: Get Your Measurement ID

1. **Go to**: https://analytics.google.com
2. **Sign in** with your Google account
3. **Click "Start measuring"** (if first time)
4. **Create Account**:
   - Account name: Converter App
   - Click Next
5. **Create Property**:
   - Property name: File Converter Pro
   - Time zone: India
   - Currency: INR
   - Click Next
6. **Business details**:
   - Choose appropriate options
   - Click Create
7. **Choose platform**: Web
8. **Set up data stream**:
   - Website URL: `https://converter-lmxu.onrender.com`
   - Stream name: Production
9. **Copy the Measurement ID** (looks like `G-XXXXXXXXXX`)

---

## Step 2: Add to Render Environment

1. **Go to Render Dashboard** → Your Service → **Environment**
2. **Add Environment Variable**:
   ```
   Name: REACT_APP_GA_MEASUREMENT_ID
   Value: G-XXXXXXXXXX
   ```
3. **Save** (triggers redeploy)

---

## Step 3: Done!

After redeploy, Google Analytics will automatically track:

### Automatic Tracking:
- ✅ **Page Views** - Every page visit
- ✅ **User Sessions** - How long users stay
- ✅ **Traffic Sources** - Where users come from
- ✅ **Device Types** - Mobile/Desktop/Tablet
- ✅ **Geographic Location** - Country, city

### Custom Events Tracked:
- ✅ **Conversions** - Format + file size
  ```
  Event: conversion
  Label: "pdf to docx"
  Value: File size in KB
  ```
- ✅ **Downloads** - When users download files
- ✅ **Feedback** - When users submit feedback

---

## Step 4: View Analytics

1. Go to https://analytics.google.com
2. Select your property
3. **Reports** → **Real-time**: See live visitors
4. **Reports** → **Events**: See conversions, downloads
5. **Reports** → **Engagement**: See popular formats

---

## What You'll See in Analytics:

### Conversions by Format:
- Most popular conversions
- Success rates
- Average file sizes

### User Behavior:
- How long they stay
- Bounce rate
- Return visitors

### Traffic:
- Daily/Weekly/Monthly visitors
- Peak usage times
- Traffic sources (Google, Direct, Social)

---

## Privacy Note:

Google Analytics is GDPR compliant when configured properly. All tracking is:
- Anonymous (no personal data)
- Aggregated statistics only
- Can be disabled by users with ad blockers

**Current setup respects user privacy while giving you valuable insights!**
