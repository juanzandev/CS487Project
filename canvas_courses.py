#!/usr/bin/env python3
"""
Canvas API Course Fetcher
A simple script to fetch and display course names from Canvas LMS
"""

import requests
import json

# Import Canvas API Configuration
try:
    from config import CANVAS_BASE_URL, API_TOKEN
except ImportError:
    print("Error: config.py not found!")
    print("Please copy config.example.py to config.py and add your API token.")
    exit(1)


def get_canvas_courses():
    """
    Fetches all courses from Canvas API and returns course data
    """
    # API endpoint for getting courses
    url = f"{CANVAS_BASE_URL}/api/v1/courses"

    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Parameters for the API call
    params = {
        "enrollment_state": "active",  # Only get active courses
        "include": ["term"],  # Include term information
        "per_page": 100  # Get up to 100 courses per page
    }

    try:
        print("Fetching courses from Canvas...")
        response = requests.get(url, headers=headers, params=params)

        # Check if request was successful
        if response.status_code == 200:
            courses = response.json()
            return courses
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None


def get_course_grade(course_id):
    """
    Fetches the current grade for a specific course
    """
    # API endpoint for getting enrollments (which includes grades)
    url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/enrollments"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "type": ["StudentEnrollment"],  # Only get student enrollments
        "include": ["grades"],  # Include grade information
        "user_id": "self"  # Get only current user's enrollment
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            enrollments = response.json()
            if enrollments and len(enrollments) > 0:
                # Get the first (should be only) enrollment
                enrollment = enrollments[0]
                grades = enrollment.get('grades', {})

                # Get current score and letter grade
                current_score = grades.get('current_score')
                current_grade = grades.get('current_grade')
                final_score = grades.get('final_score')
                final_grade = grades.get('final_grade')

                return {
                    'current_score': current_score,
                    'current_grade': current_grade,
                    'final_score': final_score,
                    'final_grade': final_grade
                }

        return None

    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None


def display_courses(courses):
    """
    Display course information in a formatted way, including grades
    """
    if not courses:
        print("No courses found or error occurred.")
        return

    print(f"\n{'='*70}")
    print(f"Found {len(courses)} course(s):")
    print(f"{'='*70}")

    for i, course in enumerate(courses, 1):
        course_name = course.get('name', 'No name available')
        course_code = course.get('course_code', 'No code')
        course_id = course.get('id', 'No ID')

        # Get term info if available
        term_name = "Unknown term"
        if 'term' in course and course['term']:
            term_name = course['term'].get('name', 'Unknown term')

        print(f"{i:2d}. {course_name}")
        print(f"    Course Code: {course_code}")
        print(f"    Course ID: {course_id}")
        print(f"    Term: {term_name}")

        # Fetch and display grade information
        print("    Fetching grade information...")
        grade_info = get_course_grade(course_id)

        if grade_info:
            current_score = grade_info.get('current_score')
            current_grade = grade_info.get('current_grade')
            final_score = grade_info.get('final_score')
            final_grade = grade_info.get('final_grade')

            # Display current grade
            if current_score is not None:
                grade_display = f"{current_score:.1f}%"
                if current_grade:
                    grade_display += f" ({current_grade})"
                print(f"    Current Grade: {grade_display}")
            elif final_score is not None:
                grade_display = f"{final_score:.1f}%"
                if final_grade:
                    grade_display += f" ({final_grade})"
                print(f"    Final Grade: {grade_display}")
            else:
                print(f"    Grade: No grade available")
        else:
            print(f"    Grade: Unable to fetch grade information")

        print("-" * 50)


def main():
    """
    Main function to run the Canvas course fetcher
    """
    print("Canvas Course Fetcher")
    print("=====================")

    # Check if API configuration is set
    if CANVAS_BASE_URL == "https://your-school.instructure.com" or API_TOKEN == "your_api_token_here":
        print("\n⚠️  CONFIGURATION NEEDED:")
        print("1. Replace CANVAS_BASE_URL with your school's Canvas URL")
        print("   Example: https://iit.instructure.com")
        print("2. Replace API_TOKEN with your Canvas API token")
        print("3. To get an API token:")
        print("   - Log into Canvas")
        print("   - Go to Account → Settings")
        print("   - Scroll to 'Approved Integrations'")
        print("   - Click '+ New Access Token'")
        print("   - Copy the generated token")
        return

    # Fetch and display courses
    courses = get_canvas_courses()
    display_courses(courses)


if __name__ == "__main__":
    main()
