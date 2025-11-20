# Contributing to Squig League

Thank you for your interest in contributing to Squig League! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue using the bug report template. Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Docker version, browser)
- Screenshots if applicable

### Suggesting Features

Feature requests are welcome! Use the feature request template and include:
- Clear description of the proposed feature
- Use case and motivation
- How it fits with the project's goals
- Any implementation ideas you have

### Pull Requests

We actively welcome pull requests!

1. **Fork the repository** and create your branch from `main`
2. **Set up development environment** - See [SETUP.md](SETUP.md) for complete instructions
3. **Make your changes** - ensure they follow the code style guidelines
4. **Test your changes** - make sure everything works as expected
5. **Commit your changes** - follow the commit format below
6. **Push to your fork** and submit a pull request

### Quick Setup

```bash
git clone https://github.com/yourusername/squig_league.git
cd squig_league
just dev
```

**For detailed setup instructions, troubleshooting, and all available commands, see [SETUP.md](SETUP.md)**

## Environment Configuration

### How It Works

`just dev` automatically creates `.env.local` from `.env.local.example` with safe defaults. No manual configuration needed for local development.

**Environment Files:**
- `.env.local` - Auto-created by `just dev` with safe defaults
- `.env.local.example` - Template with commented variables

### Security Best Practices

**✅ DO:**
- Let `just dev` auto-create `.env.local`
- Use strong, unique passwords if deploying your own instance
- Check `.env.local.example` for available configuration options

**❌ DON'T:**
- Commit `.env.local` to git (already in `.gitignore`)
- Share environment files with passwords
- Use example passwords in production

### Troubleshooting

**Environment variables not working:**
```bash
# Check configuration
just env-check

# Verify .env.local exists
ls -la .env.local

# Common issue: No spaces around = in .env files
# ✅ Correct: DB_PASSWORD=mypassword
# ❌ Wrong:   DB_PASSWORD = mypassword
```

## Code Style

### Python

- Follow **PEP 8** style guidelines
- Use **Black** formatter (line length: 88)
- Use **isort** for import sorting
- Write docstrings for functions and classes
- Use type hints where appropriate

```bash
# Format code with Black
black .

# Sort imports
isort .
```

### Commit Format

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Scopes:**
- `herald`: Herald module (blind list exchange)
- `scribe`: Scribe module (score tracking)
- `patron`: Patron module (tournament management)
- `keeper`: Keeper module (league management)
- `squire`: Squire module (personal army tracker)
- `api`: Backend API changes
- `ui`: Frontend UI changes
- `docker`: Docker configuration
- `db`: Database changes

**Examples:**
```
feat(herald): add support for custom deletion timeframes
fix(herald): correct SHA-256 hash validation
docs(readme): update installation instructions
chore(docker): upgrade PostgreSQL to version 16
```

## Code Review Process

1. All submissions require review before merging
2. Maintainers will review your PR and may request changes
3. Address review comments by pushing new commits
4. Once approved, a maintainer will merge your PR

## Project Structure

```
squig_league/
├── herald/                # Backend (JSON API)
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database operations
│   └── models.py         # Pydantic models
├── frontend/             # Frontend (Alpine.js SPA)
│   ├── index.html        # Main page
│   ├── view.html         # Exchange view
│   └── style.css         # Global styles
├── database/             # PostgreSQL initialization
│   └── init.sql          # Database schema
├── nginx/                # Nginx configuration
├── docker-compose.yml    # Base Docker config
├── docker-compose.dev.yml  # Dev overrides
└── justfile              # Command definitions
```

## Architecture

Squig League uses **frontend/backend separation**:
- **Backend** (herald/): FastAPI JSON API at `/api/herald/*`
- **Frontend** (frontend/): Alpine.js SPA for UI
- **Nginx**: Routes `/api/*` to backend, everything else to frontend

## Testing

Before submitting a PR, ensure your changes don't break existing functionality:

```bash
# Start development environment
just dev

# Manual testing checklist:
# - Test the specific feature you changed
# - Test related features that might be affected
# - Test on different browsers if UI changes
# - Verify no console errors in browser developer tools
# - Check backend logs: just logs-squig
# - Test API endpoints directly with curl if backend changes
```

### Testing Backend Changes

```bash
# Test API endpoints directly
curl -X POST http://localhost:8000/api/herald/exchange/create \
  -H "Content-Type: application/json" \
  -d '{"list_content":"Test Army List"}'

# Check health
curl http://localhost:8000/health

# View stats
curl http://localhost:8000/api/herald/stats
```

### Testing Frontend Changes

```bash
# Start services and open browser
just dev
open http://localhost:8000

# Check browser console for errors
# Test all user flows:
# 1. Create exchange
# 2. Copy URL
# 3. Open URL in incognito/private window
# 4. Submit response
# 5. Verify both lists appear
```

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Email**: ariel@ogdowscy.pl
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0.

## Recognition

Contributors will be recognized in the project documentation and release notes.

Thank you for contributing to Squig League!
