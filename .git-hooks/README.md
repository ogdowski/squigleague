# Git Hooks for Security

## Installation

Install the pre-commit hook to prevent accidentally committing secrets:

```bash
# One-time setup
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## What It Does

The pre-commit hook checks for:
- ✅ `.env` files (blocks commit)
- ✅ Password/secret/API key patterns (warns)
- ✅ IP addresses (warns for non-localhost)

## Testing

```bash
# Try to commit a .env file (should fail)
touch .env
git add .env
git commit -m "test"  # Hook will block this

# Clean up
git reset HEAD .env
rm .env
```
