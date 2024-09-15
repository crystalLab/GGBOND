# GGBOND
this is the respository for mananging project including code shares, asssests uploads etc.

# codespace ip address
<br>bash: curl ifconfig.me

# code commit
<br>bash: git add .
<br>bash: git commit -m "your any names"
<br>bash: git push origin main


# Kivy
a python framework that supports multi-touch apps and well-suits for mobile platforms.co-operate with Pygame to write game logics and Buildozer to package it for Android. 
- convert Pygame code to kivy
- use Buildozer to create APK for Android

1. set up python python virtual environment for kivy
- bash: python -m venv kivy_env
- bash: source kivy_env/bin/activate
2. install dependencies
- bash: sudo apt-get install python3-dev libgles2-mesa-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-pulseaudio
3. install kivy and additional components
- bash: pip install kivy
- bash: pip install kivy[base] kivy[media] kivy[angle] kivy[full]
4. test your kivy if it works
create a python file: app.py
<br>write code:<br>

//from kivy.app import App <br>
//from kivy.uix.label import Label<br>

//class MyApp(App):<br>
//    def build(self):
        return Label(text="Hello, Kivy!")<br>

//if __name__ == '__main__':
    MyApp().run()

5. run your python file
- bash: python app.py


# VNC in Codespace
to run the code and view within Codespace, configure VNC to achieve it
1. install VNC server (e.g. tightvncserver)
- bash: sudo apt-get install xfce4 xfce4-goodies
- bash: sudo apt-get install tightvncserver
2. set a password for VNC
- bash: vncserver
3. configure VNC server with XFCE
- bash: vncserver -kill :1
4. modify VNC startup file
- bash: vim ~/.vnc/xstartup
5. replace contents <br>
#!/bin/sh
xrdb $HOME/.Xresources <br>
startxfce4 &
6. make the file executable
- bash: chmod +x ~/.vnc/xstartup 
7. start VNC server
- bash: vncserver :1
8. access VNC server from local machine
- bash: curl ifconfig.me
9. set up an SSH tunnel to forward VNC port:
- bash: -L 5901:localhost:5901 codespace@<public_ip>
10. download VNC client (e.g RealVNC)
- bash: sudo apt-get install realvnc
11. open to the browser: localhost:5901 (or 127.0.0.1:5901)
12. test if your connection is working
- bash: python app.py



