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

class Done(Exception):
    """Gets raised once the program is done to stop it."""

class LocalServer(BaseHTTPRequestHandler):
    """Server class."""
    def do_POST(self):
        """Gets called whenever data is given through js."""
        keyboard = Controller()
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length).decode('utf-8')
        if data == "&nbsp;":
            data = " "

        if data == "init":
            for i in range(3):
                print("You have " + str(3-i) + " seconds to focus the page again...", end="\r")
                time.sleep(1)
            keyboard.tap(Key.enter)
            print("Initialized.                                          ")
        elif data == "end":
            webServer.server_close()
            print("Server stopped.")
            sys.exit()
        else:
            keyboard.tap(data)

if __name__ == "__main__":
    wait_time = 600.0 / int(input("How many inputs per 10 minutes would you like to achieve? "))

    JS_CODE = """
    //utility function
    const delay = ms => new Promise(res => setTimeout(res, ms));

    //initial signal
    $.ajax({type:'POST', url:'http://localhost:8080', data: 'init', dataType:'text'});

    setTimeout(async function() {
        //wait a tiny bit once
        await delay(500);

        //send char to press
        $.ajax({type:'POST', url:'http://localhost:8080', data:document.getElementById('text_todo').childNodes[0].innerHTML, dataType:'text'});
        //again wait a tiny bit so the remaining amount loads
        await delay(200);

        //total only becomes visible after pressing the first character
        var total = await parseInt(document.getElementById('amountRemaining').innerHTML)+1;
        console.log('total is ' + total);

        //input loop
        for (var i = 1; i < total; i++) {
            await delay(""" + str(wait_time*1000) + """);

            //send char to press
            $.ajax({type:'POST', url:'http://localhost:8080', data:document.getElementById('text_todo').childNodes[0].innerHTML, dataType:'text'});
        }

        //end signal
        $.ajax({type:'POST', url:'http://localhost:8080', data: 'end', dataType:'text'});
    }, 3000);
    """

    webServer = HTTPServer((HOST_NAME, SERVER_PORT), LocalServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")
    pyperclip.copy(JS_CODE)
    print("Code has been copied to your clipboard.\nPlease navigate to the page of your lesson.\n\
Open developer tools using ctrl+shift+i, then navigate to the Console tab.\n\
Finally, paste the code and hit enter, then focus back to the page within 3 seconds.")

    try:
        webServer.serve_forever()
    except (KeyboardInterrupt, Done):
        pass

    webServer.server_close()
    print("Server stopped.")
