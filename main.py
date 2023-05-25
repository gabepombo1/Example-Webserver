from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from urllib.parse import parse_qs
import bcrypt

PORT = 8000

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)

    # get data
    def do_GET(self):

        request_path = self.path

        print("\n----- Request Start ----->\n")
        print("request_path :", request_path)
        print("self.headers :", self.headers)
        print("<----- Request End -----\n")

        userLoginFile = open("webfiles/loginUser.html")

        self.send_response(200)
        self.end_headers()
        # encode because HTTP needs to read bytes
        self.wfile.write(userLoginFile.read().encode())

    #inserting data
    def do_POST(self):

        request_path = self.path

        print("\n----- Request Start ----->\n")
        print("request_path : %s", request_path)

        request_headers = self.headers
        content_length = request_headers['Content-Length'] #if request_headers else None
        print(content_length)
        length = int(content_length) if content_length else 0

        print("length :", length)

        content = self.rfile.read(length).decode()

        print("request_headers : %s" % request_headers)
        print("content : %s" % content)
        print("<----- Request End -----\n")

        checkParams = parse_qs(content)

        if "setphrase" in checkParams:
            salt = bcrypt.gensalt()
            phrase = checkParams["setphrase"][0]
            hashedphrase = bcrypt.hashpw(phrase.encode(), salt).decode()
            saveLoginFile = open("webfiles/saveLogin", "w")
            saveLoginFile.write(hashedphrase)
            saveLoginFile.close()
            #so you can see the salt
            print(salt.decode())

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body>Secret Phrase Set!</body></html>")

        elif "checkphrase" in checkParams:
            saveLoginFile = open("webfiles/saveLogin")
            hashedphrase = saveLoginFile.read()

            if bcrypt.checkpw(checkParams["checkphrase"][0].encode(), hashedphrase.encode()):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<html><body>Secret Phrase Matched!</body></html>")

            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<html><body>WRONG!</body></html>")

        else:
            print("ERROR: response did not contain the correct parameters")

    do_PUT = do_POST
    do_DELETE = do_GET

Handler = MyHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
