import eel

eel.init("web")
@eel.expose
def hello():
    return "hi from python :3" #put the stuff here

eel.start("index.html", size=(800,600), port=8001)