# Email Configuration for Feedback Notifications

Add these environment variables to Render:

## Option 1: Gmail (Recommended for Personal Use)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create App Password:** https://myaccount.google.com/apppasswords
3. **Add to Render Environment:**

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_password_here
ADMIN_EMAIL=your.email@gmail.com
```

## Option 2: SendGrid (Recommended for Production)

1. **Sign up:** https://sendgrid.com (free tier: 100 emails/day)
2. **Create API Key:** Settings → API Keys → Create API Key
3. **Copy the API Key** (you'll only see it once!)
4. **Add to Render Environment:**

**IMPORTANT:** For SendGrid, `SMTP_USER` is literally the word `apikey`

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_EMAIL=your.email@example.com
```

**Note:**
- `SMTP_USER` = `apikey` (exactly as written, NOT your username)
- `SMTP_PASSWORD` = Your actual SendGrid API key (starts with `SG.`)

## Option 3: Any SMTP Provider

Works with any SMTP service (Mailgun, AWS SES, etc.)

```
SMTP_SERVER=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USER=your_username
SMTP_PASSWORD=your_password
ADMIN_EMAIL=admin@yourdomain.com
```

---

## Setup Steps in Render

1. Go to https://dashboard.render.com
2. Select your Converter service
3. Click **Environment** tab
4. Click **Add Environment Variable** for each variable above
5. Click **Save Changes** (auto-redeploys)

---

## What You'll Receive

Every feedback submission sends an email:

**Subject:** New Bug - Converter App  
**Body:**
```
Type: BUG
Time: 2025-12-12T04:16:00Z

Message:
PDF conversion failed with error message

Contact: user@example.com

Metadata:
- User Agent: Mozilla/5.0...
- Page: /

Feedback ID: fb_1734068160
```

---

## Notes

- If env vars are missing, app still works (just no emails)
- Non-blocking: Email failure doesn't break feedback submission
- All emails logged to console for debugging
