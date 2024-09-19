"""
Game Development - First Stage Implementation
This module implements partial functionality for a mobile game that integrates step counting and a leaderboard feature.
The game uses the Kivy framework for the UI and the Fitbit API for fetching step data.

The app contains two classes, appAPI and appContainer:
- appAPI: to handle API inetgration
- appContainer: to construct app UI and functionalities
A Flask route is used to handle the OAuth callback

External Resources:
- Kivy Framework: https://kivy.org/doc/stable/gettingstarted/installation.html
- Fitbit API: https://python-fitbit.readthedocs.io/en/latest/
- Android Developer Health & Fitness: https://developer.android.com/health-and-fitness/guides/health-connect/migrate/comparison-guide#health-connect
"""

#import neccessary
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from jnius import autoclass
from flask import Flask, request 
from threading import Thread
from random import randint
import random
import requests
import fitbit
import webbrowser
import time
import base64 as bs

#configuration
flask_app = Flask(__name__)
#global store authorization code
auth_code = None
#set an example key and secret code to run the app in dev mode
client_id = "23PMXP"
client_secret = "88118ca41d97349452eefdd860dfd5b0"
#set random npc name to simulate users for step battles
robot_names = ["RoboBuddy", "StepMaster", "FitBot", "Walker", "StrideBot",
               "StepHero","StepLander","Rainbow","CoolerCow","MonkeyWalk"]

"""
    FIRST PART: API integration
"""
class appAPI:
    """
    A class to handle Fitbit API interactions, managing authentication and data fetching.
    """
    def __init__(self, consumer_key, consumer_secret, access_token=None, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.client = self.build_api(consumer_key, consumer_secret, access_token, refresh_token)
        

    def build_api(self, consumer_key, consumer_secret, access_token, refresh_token):
        """
        Initializes an authenticated or unauthenticated Fitbit client based on provided tokens.
        """
        unauth_client = fitbit.Fitbit(consumer_key,consumer_secret)
        authd_client = fitbit.Fitbit(consumer_key, consumer_secret,access_token=access_token, refresh_token=refresh_token)

        if access_token and refresh_token: 
            return authd_client
        else:
            return unauth_client
        
    def fetch_activity_steps(self):
        """
        Initializes data fetching structure, retrieve user's activity data in steps count.
        """
        #add header
        header = {"Authorization": f"Bearer {self.access_token}"}
        #fetch today's steps data
        res = requests.get("https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json", headers=header)
        data = res.json()
        if 'activities-steps' in data and len(data['activities-steps']) > 0:
            #get the entry data
            activityLog = data['activities-steps'][0]
            # retrieve steps count and date
            steps = activityLog.get('value','Unknown')
            date = activityLog.get('dateTime','Unknown')
            print(f"fetched steps:{steps} on date: {date}")
            return steps, date
        else:
            print("no steps data fetched")
            return None, None  

    def fetch_user_info(self):
        """
        Initializes data fetching structure, retrieve user's prifile data, especially in id, sercret code, name etc.
        """
        #fetch user's id, secret code and name (if have)
        profile_url = "https://api.fitbit.com/1/user/-/profile.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.get(profile_url, headers=headers)
        user_info = res.json()
        user_id = user_info.get('user',{}).get('encodedId')
        user_name = user_info.get('user',{}).get('fullName','Unknown User')
        print(f"user ID: {user_id}, user name: {user_name}")
        return user_id, user_name        

    @staticmethod
    def exchange_code_for_tokens(auth_code, client_id, client_secret):
        """
        Initializes data exchanging structure, after get the authorization code, use it to get access and refresh tokens.
        """
        #api endpoint
        token_url = "https://api.fitbit.com/oauth2/token"       
        #data payload
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:5000",
            "code": auth_code
        }
        #create encode credentials
        client_credentials = f"{client_id}:{client_secret}"
        encoded_credentials =bs.b64encode(client_credentials.encode()).decode()
        #headers
        headers={
            "Authorization":f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"}
        #check log exchange attempt
        print(f"attempting to exchange code {auth_code}")

        #send POST response
        res = requests.post(token_url, headers=headers, data=data)
        #handle the request
        token_data = res.json()
        access_token = token_data.get("access_token")
        print(f"access token:{access_token}")
        refresh_token = token_data.get("refresh_token")
        print(f"refresh_token:{refresh_token}")

        if res.status_code != 200:
            print(f"failed{res.status_code},{res.text}")

        return access_token, refresh_token


"""
    SECOND PART: App UI and functionalities
"""
class appContainer(App):
    """
    A class to manage the main application interface for a fitness tracking game. It handles user interactions,
    data retrieval, and displays data related to user steps and leaderboard standings.
    """
    def __init__(self, **kwargs):
        """
        Initialize the application with user-specific data structures.
        """
        super().__init__(**kwargs)
        #initialize user steps
        self.user_steps = None 
        #initialize user names
        self.user_name = ""
        #initialize user data
        self.data = []
        #initialize leaderboard data
        self.leaderboard_data = [] 

    def build(self):
        """
        Builds the UI components of the app.
        """
        #set box layput
        box = BoxLayout(orientation='vertical')
        #set inistal label text
        self.label = Label(text="fetching step data...")
        #update the label size when the text changes
        self.label.bind(texture_size=self.label.setter('size'))
        box.add_widget(self.label)

        #add inputbox for users to change their name
        #add text line
        self.input_name = TextInput(hint_text="eneter your name here", multiline=False, 
                              size_hint_y=None, height=50)
        #add button
        self.button_name = Button(text="change name", size_hint_y=None, height=50)
        #hide inputbox for name changing
        self.input_name.opacity = 0
        self.input_name.disabled = True
        self.button_name.opacity = 0
        self.button_name.disabled = True
        #bind input and button
        self.button_name.bind(on_press=self.on_submit_name)

        #if user refuse to change their name:
        self.button_decline = Button(text="keep current name", size_hint_y=None, height=50)
        self.button_decline.bind(on_press=self.name_unchange)
        self.button_decline.opacity = 0
        self.button_decline.disabled = True
        
        #if user choose to generate random name by system
        self.button_random = Button(text="generate random name", size_hint_y=None, height=50)
        self.button_random.bind(on_press=self.name_random)
        self.button_random.opacity = 0
        self.button_random.disabled = True

        #add input box to users set their steps
        #add text input
        self.input_steps = TextInput(hint_text="enter your steps here", multiline=False, 
                               size_hint_y=None, height=50)
        #add button
        self.button_steps = Button(text="change steps", size_hint_y=None, height=50)
        #hide input and button
        self.input_steps.opacity = 0
        self.input_steps.disabled = True
        self.button_steps.opacity = 0
        self.button_steps.disabled = True  
        #bind input and button
        self.button_steps.bind(on_press=self.on_submit_steps)

        #add leaderboard
        self.button_leaderboard = Button(text="view leaderboard", size_hint_y=None, height=50)
        self.button_leaderboard.bind(on_press=lambda x: self.show_leaderboard(x, None))
        box.add_widget(self.button_leaderboard)

        #add PK choice
        self.button_pk = Button(text="challenge system", size_hint_y=None, height=50)
        self.button_pk.bind(on_press=self.robot_steps)
        box.add_widget(self.button_pk)
        #add all interactive components
        box.add_widget(self.input_steps)
        box.add_widget(self.button_steps)
        box.add_widget(self.input_name)
        box.add_widget(self.button_name)
        box.add_widget(self.button_decline)
        box.add_widget(self.button_random)

        return box
    
    def on_start(self):
        """
        Called automatically when the Kivy application starts; it triggers the authentication and initial data fetch.
        """
        self.start()
    
    def start(self):
        """
        Handles the initial authentication flow by directing the user to the Fitbit authorization page.
        """
        global auth_code, client_id, client_secret  
        # Open the Fitbit authorization page in the default browser
        fitbit_authorization_url = (
            f"https://www.fitbit.com/oauth2/authorize"
            f"?response_type=code&client_id=23PMXP"
            f"&redirect_uri=http://localhost:5000"
            f"&scope=activity+profile&expires_in=604800"
        )
        webbrowser.open(fitbit_authorization_url)
        #wait for 20 seconds
        retries = 20  
        while retries > 0:
            #check if the auth_code is set
            if auth_code is not None:  
                print(f"Authorization Code Received: {auth_code}")
                break
            retries -= 1
            time.sleep(1)
      
        # when authorization code recieved, exchange for tokens
        if auth_code: 
            print(f"Authorization Code Received: {auth_code}")
            #retrieve access token and refresh token
            access_token, refresh_token = appAPI.exchange_code_for_tokens(auth_code, client_id, client_secret)

            if access_token:
                #fetch users info dynamically
                self.user_id, self.user_name = self.get_user_info(access_token)  
                #fetch steps data
                steps,date = self.get_activity_steps(access_token)

                if steps is not None and date is not None:
                    self.label.text = f"{self.user_name},you have achieved {steps} steps on {date}" 
                    if int(steps) == 0:
                        #display input box
                        self.message_show()                        
                    else:
                        self.label.text = f"you have achieved {steps} on {date}"                      
                else:
                    self.label.text = "no steps data found"     
            else:
                self.label.text = "failed to fetch access token"
    
    def get_user_info(self,access_token):
        """
        Fetches and returns user information from Fitbit API.
        """
        api = appAPI(consumer_key=client_id, 
                     consumer_secret=client_secret, 
                     access_token=access_token)
        user_id, user_name = api.fetch_user_info()
        return user_id, user_name
    
    def get_activity_steps(self, access_token):
        """
        Retrieves the number of steps taken by the user from the Fitbit API.
        """
        #api client info
        fitbit_api = appAPI(consumer_key=client_id,
                            consumer_secret=client_secret,
                            access_token=access_token)
        #call get_activity_steps
        steps, date = fitbit_api.fetch_activity_steps()
        #store user's fetched steps
        self.user_steps = int(steps)
        #return number of steps or error message
        return steps, date
    
    def robot_steps(self, instance):
        """
        Simulates a step competition against a randomly generated step count.
        """
        #generate random steps
        steps = randint(0,10000)
        #convert user steps to integer
        user_steps = int(self.user_steps)
        #compare with user's steps
        if user_steps is None:
            self.label.text = "unable to compare steps. Please enter or fetch your steps first." 
            return  
        if steps > user_steps:
            self.label.text = f"{random.choice(robot_names)} wins with {steps} steps, while you have {user_steps} steps!"
        elif steps < user_steps:
            self.label.text = f"you wins with {user_steps} steps, while {random.choice(robot_names)} has {steps} steps!"
        else:
            self.label.text = f"it's a tie! Both you and the {random.choice(robot_names)} have {steps} steps!"
        #add users to leaderboard
        self.update_leaderboard(steps)        

    def leaderboard_random(self):
        """
        Generates random entries for the leaderboard to simulate other participants.
        """
        return [
        {"name": random.choice(robot_names), "steps": random.randint(0, 10000)} 
        for _ in range(9) 
    ]

    def show_leaderboard(self, instance, robot_steps):
        """
        Displays the current leaderboard including random robots and possibly the user.
        """
        #random robot data
        self.leaderboard_data = self.leaderboard_random()
        #update leaderboard
        self.update_leaderboard(robot_steps)
        data_sorted = sorted(self.data + self.leaderboard_data, key=lambda x: x['steps'] if x['steps'] is not None else 0, reverse=True)
        #if no user in the leaderboard, add the user to it
        if not any(user['name'] == self.user_name for user in data_sorted):
            data_sorted.append({"name":self.user_name, "steps": self.user_steps})
        #add title and display    
        title = "Leaderboard:\n"
        for i, entry in enumerate(data_sorted):
            title += f"{i + 1}. {entry['name']}: {entry['steps']} steps\n"
        #update leaderboard
        self.label.text = title    

    def update_leaderboard(self, robot_steps):
        """
        Updates the leaderboard with the latest step data, as well as a list of robot data.
        """
        #firstly set user's inital data is none
        self.data = [entry for entry in self.data if entry.get('id') != self.user_id]
        #update robot steps to the leaderboard
        if robot_steps is not None:
            self.data.append({"id": self.user_id,"name": random.choice(robot_names), "steps": robot_steps})
        #add user to the leaderboard
        if self.user_steps is not None:
            self.data.append({"id": self.user_id,"name":self.user_name, "steps": self.user_steps})

    def leaderboard_robot(self):
        """
        Generates a list of robot names with random step counts to simulate a competitive environment.
        This method populates the leaderboard with synthetic data for demonstration purposes.

        Returns:
            A list of dictionaries, each containing a 'name' and 'steps' key for leaderboard entries.
        """
        #create random name and steps
        self.leaderboard_data = []
        for name in robot_names:
            steps = random.randint(0, 1000)
            self.leaderboard_data.append({"name": name, "steps": steps})
        return self.leaderboard_data    
        
    
    def message_show(self):
        """
        Displays options for the user to change their name.
        """
        self.label.text = f"hi, {self.user_name}. would you like to change your name on the app?"
        #input box visibles
        self.input_name.opacity = 1
        self.input_name.disabled = False
        self.button_name.opacity = 1
        self.button_name.disabled = False 
        self.button_decline.opacity = 1
        self.button_decline.disabled = False
        self.button_random.opacity = 1
        self.button_random.disabled = False
        
    def on_submit_steps(self, instance):
        """
        Handles the submission of manually entered steps. Validates the input and updates the user's step count.
        """
        #retrive user's input number
        num = self.input_steps.text
        if num.isdigit():
            self.user_steps = int(num)
            self.label.text = f"now your steps are {self.user_steps}"
            self.input_steps.text= "" #clear text box
            self.hide_step_input()
        else:
            #if input is invalid, generate a random steps as a fallback.
            self.user_steps = randint(0,10000)
            self.label.text = f"your enter was invalid, here is a random number auto generated: {self.user_steps}"  

    def show_steps(self):
        """
        Displays options to manually enter steps if the system did not fetch any step data.
        """
        #show the changin steps inputbox
        if hasattr(self, 'user_name') and self.user_name:
            self.label.text = f"hi, {self.user_name}. It seems you do not have walking steps today. Would you like to enter your walking steps manually?"
        else:
            self.label.text = "hi, no name user. It seems you do not have walking steps today. Would you like to enter your walking steps manually?"
        #input box visibles
        self.input_steps.opacity = 1
        self.input_steps.disabled = False
        self.button_steps.opacity = 1
        self.button_steps.disabled = False  


    def on_submit_name(self, instance):
        """
        Handles the submission of a new user name. Validates the input and updates the user's name.
        """
        #retrive user's input text
        name = self.input_name.text
        print(f"user input name: '{name}'")
        if name.strip():
            self.user_name = name
            self.label.text = f"now your name is {self.user_name}"
            #clear input box
            self.input_name.text = ""  
            #hide name change options
            self.hide_name_input()
            #run robot steps competition
            self.show_steps()   
            print("name updated successfully")
        else:
            self.label.text = f"your enter was invalid, please try again"
 

    def name_unchange(self, instance):
        """
        Handles the action when a user chooses to keep their current name.
        """
        print(f"user name: '{self.user_name}'")
        #hide name change options
        self.hide_name_input()
        #run robot steps competition
        self.show_steps() 

    def name_random(self, instance):
        """
        Assigns a randomly selected name from a predefined list of names.
        """
        #generate a random name
        self.user_name = random.choice(robot_names)
        print(f"user input name: '{self.user_name}'")
        #hide name change options
        self.hide_name_input()
        #run robot steps competition
        self.show_steps() 
        print("name updated successfully")
        
    def hide_name_input(self):
        """
        Hides the name input field and associated buttons.
        """
        #hide the name input and button
        self.input_name.opacity = 0
        self.input_name.disabled = True
        self.button_name.opacity = 0
        self.button_name.disabled = True
        self.button_decline.opacity = 0
        self.button_decline.disabled = True
        self.button_random.opacity = 0
        self.button_random.disabled = True

    def hide_step_input(self):
        """
        Hides the step input field and associated button after steps are entered.
        """
        #hide the step input box after steps are entered
        self.input_steps.opacity = 0
        self.input_steps.disabled = True
        self.button_steps.opacity = 0
        self.button_steps.disabled = True

                
"""
    THIRD PART: Flask router & run
"""
@flask_app.route('/', methods=['GET'])
def home():
    """
    A Flask route to handle the initial OAuth callback and capture the authorization code.
    """
    global auth_code
    print(f"Query Parameters: {request.args}")
    code = request.args.get('code')
    if code:
        auth_code = code
        print(f"code captured: {auth_code}")
        return f'authorization code recieved: {auth_code}'
    elif auth_code:
        print(f"code already set:{auth_code}")
        return f'code already set:{auth_code}'
    print('no authorization code captured')
    return 'no authorization code received.'
    
def run_flask():
    """
    Runs the Flask application on a dedicated thread to handle OAuth callbacks.
    """
    flask_app.run(port=5000, use_reloader=False)



if __name__ == '__main__':
    """
    This is the entry point for the application when run as a script. This section sets up and runs the main components:
    a Flask server for handling OAuth callbacks and the Kivy application for the user interface.
    """
    #handle OAuth authentication callbacks in different flask app thread
    flask_thread = Thread(target=run_flask)
    # Launch the Flask server
    flask_thread.start()
    #start the Kivy application UI
    appContainer().run()
    #when Flask thread finishes
    #ensures the Flask server properly shut-down when the Kivy app closes
    flask_thread.join()


