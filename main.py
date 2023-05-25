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

class OnlyOnce():
    valid: bool

    def __init__(self):
        self.valid = True

    def make_invalid(self):
        self.valid = False

class LocalServer(BaseHTTPRequestHandler):
    """Server class."""
    
    def send_response(self, code, message=None):
        """"Override without the log as to not clog up the terminal."""
        #self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def send_ok(self):
        self.send_response(200, "ok")       
        self.send_header('Access-Control-Allow-Origin', '*')                
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")        
        self.end_headers()
    
    def do_OPTIONS(self):           
        self.send_ok()

    def do_GET(self):
        self.send_ok()
    
    def do_POST(self):
        """Gets called whenever data is given through js."""

        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length).decode('utf-8')

        #getting amount left from data
        amount_left = data[data.rfind(" ")+1:]
        data = data[:-(len(amount_left)+1)]
        if amount_left == "":
            amount_left = -1
        else:
            amount_left = int(amount_left)
        last_batch = amount_left == len(data)

        print(f"Using \"{data}\" as data.")

        if first_tap.valid:
            print("Initialized.")
            first_tap.make_invalid()
            time.sleep(0.5)

        for c in data:
            time.sleep(wait_time)

            keyboard.tap(c)
            self.send_ok()
            #print(f"Tapped \"{c}\"")

        if last_batch:
            webServer.server_close()
            self.send_ok()
            print("Server stopped.")
            sys.exit()

if __name__ == "__main__":
    JS_CODE = """
    function sendData() {
        let toSend = document.getElementById('text_todo').childNodes[0].innerHTML + upcoming.innerHTML;
        toSend = toSend.replaceAll("&nbsp;", " ");
        count = toSend.length;
        toSend += " " + document.getElementById("amountRemaining").innerHTML;
        $.ajax({type:'POST', url:'http://localhost:8080', data:toSend, dataType:'text'});
        console.log("Sent \\"" + toSend + "\\"");
    }

    const upcoming = document.getElementById('text_todo').childNodes[1];
    const startBox = document.children[0].children[1].children[6];
    const config = { childList: true, subtree: true, attributes: true, attributeFilter: ['style'] };

    //this gets called upon the vanishing of the initial ui box
    const init = (mutationsList, observer) => {
        sendData();
    }

    const initObserver = new MutationObserver(init);
    initObserver.observe(startBox, config);

    var count;
    //this gets called whenever a correct key has been pressed on the page
    const callback = (mutationsList, observer) => {
        count--;
        if (count == 0) {
            sendData();
        }
    }
    const observer = new MutationObserver(callback);
    observer.observe(upcoming, config);
    """

    keyboard = Controller()
    first_tap = OnlyOnce()
    wait_time = 600.0 / int(input("How many inputs per 10 minutes would you like to achieve? (-1 for no delay) "))
    if wait_time < 0:
        wait_time = 0;

    webServer = HTTPServer((HOST_NAME, SERVER_PORT), LocalServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")
    pyperclip.copy(JS_CODE)
    print("Code has been copied to your clipboard.\nPlease navigate to the page of your lesson.\n\
Open developer tools using ctrl+shift+i, then navigate to the Console tab.\n\
Finally, paste the code and hit enter, then focus the page and press any button to make the box vanish.")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
