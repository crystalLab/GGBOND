from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.config import Config
import logging

logging.basicConfig(level=logging.DEBUG)
# sdl2 window provider
#Config.set('kivy', 'window_provider', 'sdl2')
Config.set('kivy','keyboard_mode','systemandmulti')
# un in headless mode (no GUI)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
#no fullscreen mode
Config.set('graphics', 'fullscreen', '0')

class Myapp(App):
    def build(self):
        Clock.schedule_once(self.stop_app, 5)
        return Label(text="Hello, Kivy")
    
    def stop_app(self, *args):
        self.stop()  # Stop the app
    
if __name__ == '__main__':
    Myapp().run()