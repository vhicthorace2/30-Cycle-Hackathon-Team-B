import argparse
import json
import os
import webbrowser
import requests


BASE_URL="https://ciap-proxy.onrender.com"
TOKEN_FILE  = os.path.expanduser("~/.ciap_token")

#Token utilities
def save_token(access_token: str, refresh_token: str = "") -> None:
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": access_token, "refresh_token": refresh_token}, f)
    print(f"Token saved to {TOKEN_FILE}")


def load_token() -> str:
    if not os.path.exists(TOKEN_FILE):
        print(f"No token found. Run --login first.")
        raise SystemExit(1)
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    return data["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


#auth utils
def do_signup(email: str, name:str, password: str, role: str) -> None:
    """Path A — step 1: create account with email/password."""
    r = requests.post(f"{BASE_URL}/auth/signup",
                      json={"email": email, "name": name, "password": password, "role":role})
    r.raise_for_status()
    print("Account created. Now run --login to get your token.")


def do_login(email: str, password: str) -> str:
    """Path A — step 2: exchange credentials for tokens."""
    r = requests.post(f"{BASE_URL}/auth/login",
                      json={"email": email, "password": password})
    r.raise_for_status()
    data = r.json()

    access_token  = data.get("accessToken") or data.get("access_token", "")
    refresh_token = data.get("refreshToken") or data.get("refresh_token", "")

    if not access_token:
        print("Login response:", json.dumps(data, indent=2))
        raise ValueError("No accessToken in response — check field names above")

    save_token(access_token, refresh_token)
    print(f"Logged in as {email}")
    return access_token


def do_connect_youtube(token: str) -> None:
   """ connect youtube """
    r = requests.get(f"{BASE_URL}/ingestion/youtube/oauth2",
                     headers=auth_headers(token),
                     allow_redirects=False)

    # API returns a redirect URL for the OAuth flow
    if r.status_code in (302, 307, 308):
        url = r.headers.get("Location", "")
    else:
        r.raise_for_status()
        data = r.json()
        # url = data.get("url") or data.get("authUrl") or data.get("redirect_url", "")
        url = (data.get("authorizationUrl") or data.get("authUrl") or data.get("url") or data.get("redirect_url") or "")

    if not url:
        print("Response:", json.dumps(r.json() if r.content else {}, indent=2))
        raise ValueError("Could not find OAuth URL in response")

    print(f"\n  Opening browser for Google consent:\n  {url}\n")
    webbrowser.open(url)
    print("  After granting access, Google will redirect back to your server.")
    print("  Your accessToken still works — no new token is issued.")


def do_google_login() -> None:
    """ path B, using direct google login"""
    r = requests.get(f"{BASE_URL}/auth/socials/oauth2/google/login",
                     allow_redirects=False)

    if r.status_code in (302, 307, 308):
        url = r.headers.get("Location", "")
    else:
        r.raise_for_status()
        data = r.json()
        url = data.get("url") or data.get("authUrl", "")

    if not url:
        raise ValueError("No OAuth URL returned")

    print(f"\n  Opening browser for Google login:\n  {url}\n")
    webbrowser.open(url)
    print("  After login, copy the accessToken from the callback response and run:")
    print(f"  echo '{{\"access_token\": \"TOKEN_HERE\"}}' > {TOKEN_FILE}")


def do_whoami(token: str) -> None:
    """Verify the token works and print your user profile."""
    r = requests.get(f"{BASE_URL}/users/me", headers=auth_headers(token))
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))


def do_refresh(token_file: str = TOKEN_FILE) -> str:
    """Rotate the access token using the stored refresh token."""
    with open(token_file) as f:
        data = json.load(f)
    refresh = data.get("refresh_token", "")
    if not refresh:
        raise ValueError("No refresh_token stored — run --login again")

    r = requests.post(f"{BASE_URL}/auth/refresh",
                      json={"refreshToken": refresh})
    r.raise_for_status()
    result = r.json()
    new_access  = result.get("accessToken") or result.get("access_token", "")
    new_refresh = result.get("refreshToken") or result.get("refresh_token", refresh)
    save_token(new_access, new_refresh)
    print("✓  Token refreshed")
    return new_access


#cli for manual testing
def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="ciap-proxy auth helper")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--signup",          action="store_true", help="Create email account")
    group.add_argument("--login",           action="store_true", help="Login with email/password")
    group.add_argument("--connect-youtube", action="store_true", help="Link YouTube to your account")
    group.add_argument("--google-login",    action="store_true", help="Login via Google OAuth")
    group.add_argument("--whoami",          action="store_true", help="Verify token & show profile")
    group.add_argument("--refresh",         action="store_true", help="Rotate access token")
    group.add_argument("--print-token",     action="store_true", help="Print stored token")

    parser.add_argument("--email",    default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--name", default="")
    parser.add_argument("--role", default="")
    parser.add_argument("--base-url", default=BASE_URL,
                        help=f"API base URL (default: {BASE_URL})")
    args = parser.parse_args()

    
    BASE_URL = args.base_url.rstrip("/")

    if args.signup:
        if not args.email or not args.password or not args.role or not args.name:
            parser.error("--signup requires --email and --password")
        do_signup(args.email, args.name, args.password, args.role)

    elif args.login:
        if not args.email or not args.password:
            parser.error("--login requires --email and --password")
        do_login(args.email, args.password)

    elif args.connect_youtube:
        token = load_token()
        do_connect_youtube(token)

    elif args.google_login:
        do_google_login()

    elif args.whoami:
        token = load_token()
        do_whoami(token)

    elif args.refresh:
        do_refresh()

    elif args.print_token:
        print(load_token())


if __name__ == "__main__":
    main()
