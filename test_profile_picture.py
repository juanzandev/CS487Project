#!/usr/bin/env python3
"""
Test script to fetch Canvas profile picture
This will help debug profile picture loading issues
"""

import requests
import os
from config import CANVAS_BASE_URL, API_TOKEN


def test_profile_api():
    """Test fetching user profile from Canvas API"""
    print("Testing Canvas Profile API...")
    print(f"Canvas URL: {CANVAS_BASE_URL}")
    print(f"API Token: {API_TOKEN[:10]}...")

    url = f"{CANVAS_BASE_URL}/api/v1/users/self/profile"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"\nMaking API request to: {url}")
        response = requests.get(url, headers=headers, timeout=10)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            profile_data = response.json()
            print(f"\nProfile Data:")
            print(f"Name: {profile_data.get('name', 'N/A')}")
            print(f"Short Name: {profile_data.get('short_name', 'N/A')}")
            print(f"Avatar URL: {profile_data.get('avatar_url', 'N/A')}")
            print(f"ID: {profile_data.get('id', 'N/A')}")

            return profile_data
        else:
            print(f"Error: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


def download_profile_picture(avatar_url, filename="profile_picture.jpg"):
    """Download the profile picture from the avatar URL"""
    if not avatar_url:
        print("No avatar URL provided")
        return False

    print(f"\nDownloading profile picture...")
    print(f"Avatar URL: {avatar_url}")

    try:
        # Make request to download image
        response = requests.get(avatar_url, timeout=10)

        print(f"Image Response Status Code: {response.status_code}")
        print(
            f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(
            f"Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")

        if response.status_code == 200:
            # Save the image
            with open(filename, 'wb') as f:
                f.write(response.content)

            file_size = os.path.getsize(filename)
            print(f"Successfully downloaded: {filename}")
            print(f"File size: {file_size} bytes")

            # Check if it's a valid image by trying to get some basic info
            if file_size > 0:
                print("File appears to be valid (non-zero size)")
                return True
            else:
                print("Warning: Downloaded file is empty")
                return False
        else:
            print(f"Failed to download image: {response.status_code}")
            print(f"Response Text: {response.text}")
            return False

    except Exception as e:
        print(f"Exception downloading image: {e}")
        return False


def main():
    print("=" * 50)
    print("Canvas Profile Picture Test")
    print("=" * 50)

    # Test profile API
    profile_data = test_profile_api()

    if profile_data:
        avatar_url = profile_data.get('avatar_url')
        if avatar_url:
            # Try to download the picture
            success = download_profile_picture(avatar_url)
            if success:
                print(f"\n✅ Profile picture test PASSED!")
                print(f"Check the downloaded file: profile_picture.jpg")
            else:
                print(f"\n❌ Profile picture download FAILED!")
        else:
            print(f"\n⚠️  No avatar URL found in profile data")
    else:
        print(f"\n❌ Profile API test FAILED!")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
