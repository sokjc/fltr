# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Gmail promotional email filter tool (`fltr`) that automatically identifies and labels promotional emails for manual review. The tool uses the Gmail API to scan emails and applies intelligent filtering based on keywords, sender patterns, and content analysis.

## Architecture

The codebase consists of a single Python file:
- `main.py` - Contains the `GmailPromoFilter` class that handles Gmail API authentication, email analysis, and promotional email management

## Key Components

### GmailPromoFilter Class
- **Authentication**: Uses OAuth2 flow with Google's Gmail API, storing credentials in `token.json`
- **Label Management**: Creates and manages a "Promotional-Review" label for flagged emails
- **Email Analysis**: Uses keyword matching and sender pattern recognition to identify promotional content
- **Batch Operations**: Supports bulk labeling, deletion, and label removal operations

### Authentication Requirements
- Requires `credentials.json` file (Google OAuth2 client secrets)
- Generates `token.json` for subsequent API calls
- Uses Gmail API scope: `https://www.googleapis.com/auth/gmail.modify`

## Common Commands

### Setup and Installation
```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # or `uv shell`
```

### Running the Tool
```bash
# Run with uv
uv run python main.py

# Or activate environment first
source .venv/bin/activate
python main.py
```

### Dependencies
The project uses uv for dependency management. Dependencies are defined in `pyproject.toml`:
- `google-api-python-client` - Gmail API client
- `google-auth-httplib2` - HTTP transport for Google Auth
- `google-auth-oauthlib` - OAuth2 flow for Google APIs

## Security Considerations

- Never commit `credentials.json` or `token.json` files
- The tool has Gmail modify permissions - use carefully
- Always test with small batches before bulk operations
- Review labeled emails before bulk deletion

## Email Classification Logic

- **Promotional Score System**: Accumulates points based on keywords, sender patterns, and content
- **Whitelist Protection**: Important senders (banks, receipts, security alerts) are excluded
- **Threshold**: Emails with score ≥ 3 are flagged as promotional
- **Pattern Matching**: Uses regex patterns for sender identification (noreply@, marketing@, etc.)