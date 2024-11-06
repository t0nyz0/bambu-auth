import requests
import json
import certifi
import cloudscraper

# Prompt the user for their Bambu Lab username and password
bambuUsername = input("Enter your Bambu Lab username: ")
bambuPassword = input("Enter your Bambu Lab password: ")

# Define the User-Agent and other common headers
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
headers = {
    "Content-Type": "application/json",
    "User-Agent": user_agent
}

# Remove the hard-coded cookie, because this is annoying with testing
headers.pop("Cookie", None)

# cloudscraper session
scraper = cloudscraper.create_scraper()

# Perform the login request with custom headers
auth_payload = {
    "account": bambuUsername,
    "password": bambuPassword,
    "apiError": ""
}

auth_response = scraper.post(
    "https://bambulab.com/api/sign-in/form",
    headers=headers,
    json=auth_payload,
    verify=certifi.where()
)

# Check if authentication was successful
auth_json = auth_response.json()
if not auth_json.get("success"):
    print("Authentication failed, attempting code verification")

    # Send the verification code request
    send_code_payload = {
        "email": bambuUsername,
        "type": "codeLogin"
    }

    # ---------------------------------------
    # User is using verify code
    #----------------------------------------
    if auth_json.get("loginType") == "verifyCode":
        send_code_response = scraper.post(
            "https://api.bambulab.com/v1/user-service/user/sendemail/code",
            headers=headers,
            json=send_code_payload
        )
        if send_code_response.status_code == 200:
            print("Verification code sent successfully. Check your email.")
        else:
            print("Failed to send verification code.")
            print("Response:", send_code_response.text)
            exit(1)

        verify_code = input("Enter your access code: ")
        verify_payload = {
            "account": bambuUsername,
            "code": verify_code
        }
        api_response = scraper.post(
            "https://api.bambulab.com/v1/user-service/user/login",
            headers=headers,
            json=verify_payload,
            verify=certifi.where()
        )
        print("Step 2 - API verify code response:", api_response.text)

        api_token = api_response.json()
        if api_token:
            token = api_token.get("accessToken")

        if not token:
            print("Failed to extract token")
            exit(1)

    # ---------------------------------------
    # User is using MFA (TFA)
    #----------------------------------------
    elif auth_json.get("loginType") == "tfa":
        tfa_auth = auth_json.get("tfaKey")
        tfa_code = input("Enter your MFA access code: ")
        verify_payload = {
            "tfaKey": tfa_auth,
            "tfaCode": tfa_code
        }
        print("payload: ", verify_payload)
        api2_response = scraper.post(
            "https://bambulab.com/api/sign-in/tfa",
            headers=headers,
            json=verify_payload,
            verify=certifi.where()
        )
        print("Step 2 - API MFA response:", api2_response.text)

        cookies = api2_response.cookies.get_dict()
        token_from_tfa = cookies.get("token")
        print("tokenFromTFA:", token_from_tfa)

        token = token_from_tfa

        if not token:
            print("Failed to extract token")
            exit(1)

    else:
        print("Unknown loginType:", auth_json.get("loginType"))
        exit(1)

else:
    # If authentication was successful in the first attempt, get the token from the JSON response
    token = auth_json.get("accessToken")

if not token:
    print("Unable to authenticate or verify. Exiting...")
    exit(1)

# Perform the API request to fetch the image with custom headers
headers["Authorization"] = f"Bearer {token}"
api_response = scraper.get(
    "https://api.bambulab.com/v1/user-service/my/tasks",
    headers=headers
)

# Print the API response for debugging
print("API to fetch info:", api_response.text)

# Check if the API request was successful
if api_response.status_code != 200:
    print("API request failed")
    exit(1)

# Extract and display the relevant information
api_json = api_response.json()
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
