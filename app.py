from kivy import App
from kivy import Label

class Myapp(App):
    def build(self):
        return Label(text="Hello, Kivy")
    
if __name__ == '__main__':
    Myapp().run()