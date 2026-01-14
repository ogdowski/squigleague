# OAuth Setup Guide

This guide walks you through setting up Google and Discord OAuth for Squig League.

## Table of Contents
- [Google OAuth Setup](#google-oauth-setup)
- [Discord OAuth Setup](#discord-oauth-setup)
- [Environment Configuration](#environment-configuration)
- [Testing OAuth](#testing-oauth)

---

## Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name: `Squig League` (or your preferred name)
4. Click **Create**

### Step 2: Enable Google+ API

1. In the Google Cloud Console, navigate to **APIs & Services** → **Library**
2. Search for "Google+ API" or "Google People API"
3. Click on it and press **Enable**

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (unless you have a Google Workspace account)
3. Click **Create**

**Fill in the required fields:**
- **App name:** `Squig League`
- **User support email:** Your email address
- **App logo:** (Optional) Upload your app logo
- **Application home page:** `http://localhost` (for local dev) or `https://squigleague.com` (for production)
- **Authorized domains:**
  - For local: leave empty
  - For production: `squigleague.com`
- **Developer contact email:** Your email address

4. Click **Save and Continue**

**Scopes:**
5. Click **Add or Remove Scopes**
6. Select these scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
7. Click **Update** → **Save and Continue**

**Test Users (for development):**
8. Add your email address as a test user
9. Click **Save and Continue** → **Back to Dashboard**

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Application type:** `Web application`
4. **Name:** `Squig League Web Client`

**Authorized JavaScript origins:**
```
http://localhost
http://localhost:80
```

**Authorized redirect URIs:**
```
http://localhost/api/auth/oauth/google/callback
```

For production, also add:
```
https://squigleague.com/api/auth/oauth/google/callback
https://www.squigleague.com/api/auth/oauth/google/callback
```

5. Click **Create**
6. **Copy the Client ID and Client Secret** - you'll need these!

---

## Discord OAuth Setup

### Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Enter name: `Squig League`
4. Accept the terms and click **Create**

### Step 2: Configure General Information

1. In the **General Information** tab:
   - **Name:** `Squig League`
   - **Description:** `Warhammer Age of Sigmar matchup and tournament platform`
   - **App Icon:** (Optional) Upload your app icon
   - **Tags:** `gaming`, `warhammer` (optional)

2. Copy the **Application ID** (this is your Client ID)

### Step 3: Configure OAuth2

1. Go to the **OAuth2** tab in the left sidebar
2. Click **Add Redirect** under **Redirects**

**Add these redirect URIs:**
```
http://localhost/api/auth/oauth/discord/callback
```

For production:
```
https://squigleague.com/api/auth/oauth/discord/callback
https://www.squigleague.com/api/auth/oauth/discord/callback
```

3. Click **Save Changes**

### Step 4: Get Client Secret

1. In the **OAuth2** tab, under **Client Information**
2. Click **Reset Secret** (or view existing secret)
3. **Copy the Client Secret** - you'll need this!

### Step 5: Configure OAuth2 Scopes

In your application, these scopes will be automatically requested:
- `identify` - Get user's Discord username, avatar, and ID
- `email` - Get user's email address

---

## Environment Configuration

### Local Development (.env.local)

Add these variables to your `.env.local` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz

# Discord OAuth
DISCORD_CLIENT_ID=123456789012345678
DISCORD_CLIENT_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

### Production (.env.prod)

Add the same variables to `.env.prod` with your production OAuth credentials:

```bash
# Google OAuth (Production)
GOOGLE_CLIENT_ID=your-production-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-production-client-secret

# Discord OAuth (Production)
DISCORD_CLIENT_ID=your-production-client-id
DISCORD_CLIENT_SECRET=your-production-client-secret
```

**Important Notes:**
- Keep these secrets secure and never commit them to git
- Use different OAuth applications for development and production
- Production redirect URIs must use HTTPS

---

## Restart Services

After adding the credentials, restart your services:

```bash
# Local development
just down
just up

# Or manually
docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml down
docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml up -d
```

---

## Testing OAuth

### Test Google Login

1. Go to `http://localhost/login`
2. Click **Continue with Google**
3. You should be redirected to Google's login page
4. Sign in with your Google account
5. Grant permissions
6. You should be redirected back and logged in

### Test Discord Login

1. Go to `http://localhost/login`
2. Click **Continue with Discord**
3. You should be redirected to Discord's authorization page
4. Click **Authorize**
5. You should be redirected back and logged in

---

## Troubleshooting

### Google OAuth Issues

**Error: "redirect_uri_mismatch"**
- Solution: Make sure the redirect URI in Google Cloud Console exactly matches `http://localhost/api/auth/oauth/google/callback`

**Error: "Access blocked: This app's request is invalid"**
- Solution: Add your email as a test user in the OAuth consent screen

**Error: "Google+ API has not been used in project"**
- Solution: Enable the Google+ API or Google People API in the API Library

### Discord OAuth Issues

**Error: "Invalid redirect_uri"**
- Solution: Check that the redirect URI in Discord Developer Portal matches `http://localhost/api/auth/oauth/discord/callback`

**Error: "Invalid client_id"**
- Solution: Make sure you're using the Application ID from Discord, not the Client Secret

**Error: "User does not have email"**
- Solution: Some Discord users don't have verified emails. The app handles this by creating a placeholder email.

### General Issues

**OAuth buttons don't appear**
- Check that the environment variables are set correctly
- Restart the backend container: `docker-compose restart backend`
- Check backend logs: `docker-compose logs backend`

**"OAuth not configured" error**
- The backend checks if credentials are set. If empty, OAuth is disabled
- Verify environment variables are loaded: `docker-compose exec backend env | grep GOOGLE`

**Token not stored after redirect**
- Check browser console for errors
- Verify the OAuth callback route is registered: `http://localhost/oauth/callback`
- Check that localStorage is not disabled in your browser

---

## Production Deployment

### Additional Steps for Production

1. **Update OAuth Applications:**
   - Add production redirect URIs to both Google and Discord
   - Use HTTPS URLs only

2. **Update Environment Variables:**
   - Set production credentials in `.env.prod`
   - Never use development credentials in production

3. **Publish OAuth Consent Screen (Google):**
   - In Google Cloud Console, go to **OAuth consent screen**
   - Click **Publish App** to remove the "unverified app" warning
   - This may require verification from Google if you request sensitive scopes

4. **Update CORS Origins:**
   - Make sure your production domains are in `CORS_ORIGINS` in `backend/app/config.py`

---

## Security Best Practices

1. **Keep Secrets Secure:**
   - Never commit `.env.local` or `.env.prod` to git
   - Use different credentials for development and production
   - Rotate secrets periodically

2. **Validate Redirect URIs:**
   - Only add exact redirect URIs you control
   - Never use wildcards in production

3. **Monitor OAuth Usage:**
   - Check Google Cloud Console and Discord Developer Portal for unusual activity
   - Set up usage quotas and alerts

4. **Handle Token Expiration:**
   - OAuth tokens can expire
   - The app stores access and refresh tokens for future token refresh (implementation pending)

---

## Need Help?

- Google OAuth: [https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)
- Discord OAuth: [https://discord.com/developers/docs/topics/oauth2](https://discord.com/developers/docs/topics/oauth2)
- FastAPI OAuth: [https://httpx-oauth.readthedocs.io/](https://httpx-oauth.readthedocs.io/)
