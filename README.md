# Kibana & Slack Error Monitoring Bot

An automated monitoring tool designed to track Kibana HTTP search logs and prebook errors sequentially. If the error threshold is breached, it sends detailed alert notifications to Slack.

## Features
- **Multi-Stage Analysis:** Monitors general search endpoint statuses first; triggers root-cause analysis if error rate exceeds thresholds.
- **Configurable Thresholds:** Easily adjust error percentages and contract slugs via environment variables.
- **Slack Integration:** Posts clean, structured alert messages to specified Slack webhooks.

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/slack-kibana-bot.git](https://github.com/YOUR_USERNAME/slack-kibana-bot.git)
   cd slack-kibana-bot

