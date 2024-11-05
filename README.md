# Bambu Auth MFA and Verification authentication example

This test harness will give you an idea how to login to the Bambu Labs API via MFA (TFA) and when they require the user to respond to verification codes sent to their email. 

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
