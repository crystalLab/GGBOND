# StepLand Development Guide - First Stage Implementation README

## Overview
This module implements partial functionality for a mobile game that integrates step counting from users' google FitBit account, and a leaderboard feature using the Kivy framework for UI.

## Prerequisites
- Python 3.7 or newer
- Kivy
- Flask
- Requests library
- Pyjnius (for Andriod functionality)

## Installation
1. Install Python Dependencies: Ensure Python 3.7+ is installed, then install the required Python libraries using pip:
- pip install kivy flask request pyjnius
2. Kivy environment setup: <br>
- pip install kivy[base] kivy[media] //or kivy[full] if you like
- python -m venv kivy_venv
- source kivy_venv/bin/activate - Linux, MacOS
- source kivy_venv/Scripts/activate - Windows bash
- kivy_venv/Scripts/activate - Windows
3. Fitbit API setup:
- register your application at Fitbit Developer to obtain your client_id and client_secret
- Set the callback URL to http://localhost:5000 during the Fitbit app registration process
- the game.py has provided simulated user data, you can use it for testing

## Structure
appAPI: Manages API interactions, specifically authentication and data fetching from Fitbit. <br>
appContainer: Constructs the application UI and integrates functionalities such as step data display and leaderboard. <br>
A Flask route is used to handle OAuth callbacks from Fitbit authentication.

## Running Application
1. Start the Flask Server:<br>Run the Flask server which handles the OAuth callbacks. This server must be running before you start the Kivy application:
- python -m flask run --port=5000
2. Execute the Kivy Application: <br>In a separate terminal, run the Kivy application:
- python path_to_script.py
(replace path_to_script with the path to your python script)
3. Authorize with Fitbit: <br>When you run the Kivy application, your default web browser will open the Fitbit authorization page. Log in with your Fitbit credentials and authorize the app. The authorization code will be automatically handled by the Flask server.
4. Interact with the Game: <br>Use the Kivy UI to interact with the game. You can view your step count, change your user name, and view the leaderboard.

## External Resources
- Kivy Framework: https://kivy.org/doc/stable/gettingstarted/installation.html
- Fitbit API: https://python-fitbit.readthedocs.io/en/latest/
- Android Developer Health & Fitness: https://developer.android.com/health-and-fitness/guides/health-connect/migrate/comparison-guide#health-connect

## Data Code Dependencies
- Fitbit API in Python: <br>
Quickstart, https://python-fitbit.readthedocs.io/en/latest/ <br>
get_all_activity_types: https://dev.fitbit.com/build/reference/web-api/activity/get-all-activity-types/ <br>
get_activity_log, https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/ <br>
get_profile, https://dev.fitbit.com/build/reference/web-api/user/get-profile/


## Known Issues
Ensure that the Flask server is running before starting the Kivy application to avoid connection issues. <br>
The app requires internet access to fetch data from the Fitbit API and to handle OAuth authentication.