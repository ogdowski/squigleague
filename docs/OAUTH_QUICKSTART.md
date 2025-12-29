# OAuth Quick Start

## TL;DR - Get OAuth Working in 5 Minutes

### Google OAuth

1. **Create Project:** [console.cloud.google.com](https://console.cloud.google.com/) → New Project
2. **Enable API:** APIs & Services → Library → Enable "Google+ API"
3. **OAuth Consent:** APIs & Services → OAuth consent screen → External → Fill basic info
4. **Create Credentials:** APIs & Services → Credentials → Create OAuth Client ID → Web application
   - Redirect URI: `http://localhost/api/auth/oauth/google/callback`
5. **Copy credentials** and add to `.env.local`:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
   ```

### Discord OAuth

1. **Create App:** [discord.com/developers/applications](https://discord.com/developers/applications) → New Application
2. **Get Client ID:** General Information → Copy Application ID
3. **Add Redirect:** OAuth2 → Redirects → Add:
   - `http://localhost/api/auth/oauth/discord/callback`
4. **Get Secret:** OAuth2 → Reset Secret → Copy
5. **Add to `.env.local`:**
   ```bash
   DISCORD_CLIENT_ID=your-client-id
   DISCORD_CLIENT_SECRET=your-secret
   ```

### Restart and Test

```bash
just down && just up
```

Go to `http://localhost/login` and click the OAuth buttons!

---

## Redirect URIs Reference

### Development (localhost)

**Google:**
```
http://localhost/api/auth/oauth/google/callback
```

**Discord:**
```
http://localhost/api/auth/oauth/discord/callback
```

### Production

**Google:**
```
https://squigleague.com/api/auth/oauth/google/callback
https://www.squigleague.com/api/auth/oauth/google/callback
```

**Discord:**
```
https://squigleague.com/api/auth/oauth/discord/callback
https://www.squigleague.com/api/auth/oauth/discord/callback
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| `redirect_uri_mismatch` | Copy-paste redirect URI exactly as shown above |
| `Access blocked` (Google) | Add your email as test user in OAuth consent screen |
| `Invalid client_id` (Discord) | Use Application ID, not Client Secret |
| OAuth buttons don't show | Restart backend: `docker-compose restart backend` |

---

See [OAUTH_SETUP.md](./OAUTH_SETUP.md) for detailed instructions.
