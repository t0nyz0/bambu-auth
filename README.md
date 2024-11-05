# Bambu Labs Auth MFA and Verification authentication example

This test harness demonstrates how to log into the Bambu Labs API using multi-factor authentication (MFA) or email verification codes when required and displays basic print information.

## Features

- **User Authentication**: Prompts for username and password for login.
- **Multi-factor Authentication Support**: Handles both email verification codes and MFA (Two-Factor Authentication).
- **Task Retrieval**: Once logged in, retrieves details about your tasks including model title, weight, cost time, device name, and more.

## Prerequisites

- **Python 3.x**
- **Requests Library**: Install via `pip install requests`

## Usage

1. **Clone this repository** or copy the script.

2. **Run the script**:
   ```bash
   python auth.py
