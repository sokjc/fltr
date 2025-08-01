# Gmail Promotional Email Filter (fltr)

A Python tool that automatically identifies and labels promotional emails in Gmail for manual review before deletion.

## Features

- Scans Gmail for promotional emails using intelligent keyword and pattern matching
- Labels suspected promotional emails for manual review
- Supports bulk operations (delete, unlabel)
- Protects important emails with whitelist filtering
- Interactive command-line interface

## Setup

### 1. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Create Google API Credentials

1. **Go to Google Cloud Console**: Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)

2. **Create or Select a Project**:
   - Click on the project dropdown at the top
   - Create a new project or select an existing one

3. **Enable Gmail API**:
   - Go to "APIs & Services" ’ "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

4. **Create Credentials**:
   - Go to "APIs & Services" ’ "Credentials"
   - Click "Create Credentials" ’ "OAuth client ID"
   - If prompted, configure the OAuth consent screen first:
     - Choose "External" user type
     - Fill in required fields (app name, user support email, developer email)
     - Add your email to test users
   - For application type, select "Desktop application"
   - Give it a name (e.g., "Gmail Filter Tool")
   - Click "Create"

5. **Download Credentials**:
   - Click the download button () next to your newly created OAuth client
   - Save the file as `credentials.json` in the project root directory

### 3. First Run Authentication

```bash
# Run the tool
uv run python main.py
```

On first run, the tool will:
- Open your browser for Google OAuth authentication
- Ask you to sign in and grant permissions
- Save authentication tokens to `token.json` for future use

## Usage

The tool provides an interactive menu with these options:

1. **Scan and label promotional emails** - Analyzes recent emails and labels suspected promotional content
2. **Show summary of labeled emails** - Displays a list of emails marked as promotional
3. **Bulk delete all labeled emails** - Permanently deletes all emails with the promotional label
4. **Remove promotional labels** - Removes labels but keeps emails in inbox
5. **Exit** - Quit the application

### Safety Features

- **Whitelist Protection**: Important senders (banks, receipts, security alerts) are automatically excluded
- **Manual Review**: Emails are only labeled, not automatically deleted
- **Confirmation Prompts**: Bulk operations require user confirmation
- **Scoring System**: Uses intelligent scoring to reduce false positives

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The tool requires Gmail modify permissions to label and delete emails
- Always review labeled emails before bulk deletion
- Test with small batches first

## Email Classification

The tool identifies promotional emails using:

- **Keyword Matching**: Looks for promotional terms in subject and content
- **Sender Patterns**: Identifies promotional sender patterns (noreply@, marketing@, etc.)
- **Content Analysis**: Checks for unsubscribe links and promotional language
- **Scoring System**: Accumulates points based on promotional indicators
- **Whitelist Filtering**: Protects important communications

## Troubleshooting

- **"File not found: credentials.json"**: Follow the setup steps above to create API credentials
- **Authentication errors**: Delete `token.json` and re-authenticate
- **Permission errors**: Ensure your Google account has access to the Gmail you want to filter
- **API quota exceeded**: The tool respects Gmail API limits; wait and try again later