import requests
import json
import certifi
import cloudscraper
from requests.exceptions import HTTPError

# Prompt the user for their Bambu Lab username and password
bambuUsername = input("Enter your Bambu Lab username: ")
bambuPassword = input("Enter your Bambu Lab password: ")

# Slicer headers
headers = {
    'User-Agent': 'bambu_network_agent/01.09.05.01',
    'X-BBL-Client-Name': 'OrcaSlicer',
    'X-BBL-Client-Type': 'slicer',
    'X-BBL-Client-Version': '01.09.05.51',
    'X-BBL-Language': 'en-US',
    'X-BBL-OS-Type': 'linux',
    'X-BBL-OS-Version': '6.2.0',
    'X-BBL-Agent-Version': '01.09.05.01',
    'X-BBL-Executable-info': '{}',
    'X-BBL-Agent-OS-Type': 'linux',
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

scraper = cloudscraper.create_scraper(browser={'custom': 'chrome'})

# Perform the login request with custom headers
def login():
    auth_payload = {
        "account": bambuUsername,
        "password": bambuPassword,
        "apiError": ""
    }

    try:
        auth_response = scraper.post(
            "https://api.bambulab.com/v1/user-service/user/login",
            headers=headers,
            json=auth_payload,
            verify=certifi.where()
        )
        auth_response.raise_for_status()
        if auth_response.text.strip() == "":
            raise ValueError("Empty response from server, possible Cloudflare block.")
        auth_json = auth_response.json()

        # If login is successful
        if auth_json.get("success"):
            return auth_json.get("accessToken")

        # Handle additional authentication scenarios
        login_type = auth_json.get("loginType")
        if login_type == "verifyCode":
            return handle_verification_code()
        elif login_type == "tfa":
            return handle_mfa(auth_json.get("tfaKey"))
        else:
            raise ValueError(f"Unknown login type: {login_type}")

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}. Response content: {auth_response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

# Handle verification
def handle_verification_code():
    send_code_payload = {
        "email": bambuUsername,
        "type": "codeLogin"
    }

    try:
        send_code_response = scraper.post(
            "https://api.bambulab.com/v1/user-service/user/sendemail/code",
            headers=headers,
            json=send_code_payload,
            verify=certifi.where()
        )
        send_code_response.raise_for_status()
        print("Verification code sent successfully. Please check your email.")
        verify_code = input("Enter your access code: ")

        verify_payload = {
            "account": bambuUsername,
            "code": verify_code
        }
        verify_response = scraper.post(
            "https://api.bambulab.com/v1/user-service/user/login",
            headers=headers,
            json=verify_payload,
            verify=certifi.where()
        )
        verify_response.raise_for_status()
        if verify_response.text.strip() == "":
            raise ValueError("Empty response from server during verification, possible Cloudflare block.")
        return verify_response.json().get("accessToken")

    except HTTPError as http_err:
        print(f"HTTP error occurred during verification: {http_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error during verification: {json_err}. Response content: {verify_response.text}")
    except Exception as err:
        print(f"Other error occurred during verification: {err}")
    return None

# Handle MFA scenario
def handle_mfa(tfa_key):
    tfa_code = input("Enter your MFA access code: ")
    verify_payload = {
        "tfaKey": tfa_key,
        "tfaCode": tfa_code
    }

    try:
        tfa_response = scraper.post(
            "https://bambulab.com/api/sign-in/tfa",
            headers=headers,
            json=verify_payload,
            verify=certifi.where()
        )
        tfa_response.raise_for_status()
        if tfa_response.text.strip() == "":
            raise ValueError("Empty response from server during MFA, possible Cloudflare block.")
        cookies = tfa_response.cookies.get_dict()
        return cookies.get("token")

    except HTTPError as http_err:
        print(f"HTTP error occurred during MFA: {http_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error during MFA: {json_err}. Response content: {tfa_response.text}")
    except Exception as err:
        print(f"Other error occurred during MFA: {err}")
    return None

# Execute the login
access_token = login()

if not access_token:
    print("Unable to authenticate or verify. Exiting...")
    exit(1)

# Perform the API request to fetch information with custom headers
headers["Authorization"] = f"Bearer {access_token}"
try:
    api_response = scraper.get(
        "https://api.bambulab.com/v1/user-service/my/tasks",
        headers=headers,
        verify=certifi.where()
    )
    api_response.raise_for_status()
    if api_response.text.strip() == "":
        raise ValueError("Empty response from server during API request, possible Cloudflare block.")
    api_json = api_response.json()

    # Extract and display relevant information
    if api_json:
        hits = api_json.get("hits", [{}])[0]
        image_url = hits.get("cover")
        model_title = hits.get("title")
        model_weight = hits.get("weight")
        model_cost_time = hits.get("costTime")
        total_prints = api_json.get("total")
        device_name = hits.get("deviceName")
        device_model = hits.get("deviceModel")
        bed_type = hits.get("bedType")

        # Output the results
        print("Image URL:", image_url)
        print("Model Title:", model_title)
        print("Model Weight:", model_weight)
        print("Model Cost Time:", model_cost_time)
        print("Total Prints:", total_prints)
        print("Device Name:", device_name)
        print("Device Model:", device_model)
        print("Bed Type:", bed_type)
    else:
        print("Failed to parse API response.")

except HTTPError as http_err:
    print(f"HTTP error occurred during API request: {http_err}")
except json.JSONDecodeError as json_err:
    print(f"JSON decode error during API request: {json_err}. Response content: {api_response.text}")
except Exception as err:
    print(f"Other error occurred during API request: {err}")
    exit(1)
