from kivy_env import App
from kivy_env import Label

class Myapp(App):
    def build(self):
        return Label(text="Hello, Kivy")
    
if __name__ == '__main__':
    Myapp().run()