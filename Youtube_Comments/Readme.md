# 🧹 YouTube Toxic Comment Cleaner

This project automatically detects and deletes **toxic, negative, or harmful comments** from a specific YouTube video using AI-based sentiment analysis and keyword filtering. It utilizes **Google YouTube Data API**, **Detoxify**, **TextBlob**, and logs all actions in a structured Excel report.

---

## 🚀 Features

- 🔐 OAuth 2.0 authentication with YouTube Data API v3
- 💬 Fetch up to 100+ comments from any YouTube video
- 🤖 Detects toxic comments using [Detoxify](https://github.com/unitaryai/detoxify)
- 💡 Analyzes sentiment using [TextBlob](https://textblob.readthedocs.io/)
- 🔎 Filters comments based on custom **negative keywords**
- 🗑️ Automatically deletes or moderates toxic/negative comments
- 📄 Logs results in a downloadable Excel file (`deleted_comments_log.xlsx`)

---

## 📁 Project Structure

```plaintext
├── main.py                      # Main script for authentication, fetching, analysis, and deletion
├── requirements.txt             # All necessary Python packages
├── deleted_comments_log.xlsx    # Log of processed and deleted comments
├── client_secrets.json          # OAuth2 credentials (NOT INCLUDED here for security)
