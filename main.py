from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import sys
import subprocess
import pkg_resources

#make sure additional packages are installed
required = {'pyperclip', 'pynput'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    PYTHON = sys.executable
    subprocess.check_call([PYTHON, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

import pyperclip
from pynput.keyboard import Key, Controller

HOST_NAME = "localhost"
SERVER_PORT = 8080

class Current():
    letter: str
    amount_left: int

    def __init__(self, s, n):
        self.letter = s
        self.amount_left = n

class OnlyOnce():
    valid: bool

    def __init__(self):
        self.valid = True

    def make_invalid(self):
        self.valid = False

class LocalServer(BaseHTTPRequestHandler):
    """Server class."""
    def do_POST(self):
        """Gets called whenever data is given through js."""
        keyboard = Controller()
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length).decode('utf-8')

        if data == "init":
            for i in range(3):
                print("You have " + str(3-i) + " seconds to focus the page again...", end="\r")
                time.sleep(1)
            keyboard.tap(Key.enter)
            print("Initialized.                                          ")
        else:
            if first_tap.valid:
                #set len to 1 (object has to be changed without assignment)
                first_tap.make_invalid()
                time.sleep(0.5)
            time.sleep(wait_time)
            #first argument that's given is the letter. The second one is amountRemaining.
            split_data = data.split(' ')
            highlighted = Current(split_data[0], None)
            if len(split_data) > 1:
                highlighted.amount_left = split_data[1]

            if highlighted.letter == "&nbsp;":
                highlighted.letter = " "

            if highlighted.letter != '':
                keyboard.tap(highlighted.letter)

            if highlighted.amount_left == '0':
                webServer.server_close()
                print("Server stopped.")
                sys.exit()

if __name__ == "__main__":
    JS_CODE = """
    const targetNode = document.getElementById("text_todo");
    const config = { childList: true, subtree: true };

    //this gets called whenever a correct key has been pressed on the page
    const callback = (mutationsList, observer) => {
        $.ajax({type:'POST', url:'http://localhost:8080', data:document.getElementById('text_todo').childNodes[0].innerHTML + ' ' + String(document.getElementById("amountRemaining").innerHTML), dataType:'text'});
    }
    const observer = new MutationObserver(callback);
    observer.observe(targetNode, config);

    //initial signal
    $.ajax({type:'POST', url:'http://localhost:8080', data: 'init', dataType:'text'});

    //do this after 3 seconds
    setTimeout(function() {
        //send first char to press
        $.ajax({type:'POST', url:'http://localhost:8080', data:document.getElementById('text_todo').childNodes[0].innerHTML, dataType:'text'});
    }, 3000);
    """

    first_tap = OnlyOnce()
    wait_time = 600.0 / int(input("How many inputs per 10 minutes would you like to achieve? (-1 for no delay) "))
    if wait_time < 0:
        wait_time = 0;

    webServer = HTTPServer((HOST_NAME, SERVER_PORT), LocalServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")
    pyperclip.copy(JS_CODE)
    print("Code has been copied to your clipboard.\nPlease navigate to the page of your lesson.\n\
Open developer tools using ctrl+shift+i, then navigate to the Console tab.\n\
Finally, paste the code and hit enter, then focus back to the page within 3 seconds.")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
