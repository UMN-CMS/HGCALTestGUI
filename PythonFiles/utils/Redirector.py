import http.server
import socketserver
import sys
import argparse



def redirect_handler_factory(url):
    """
    Returns a request handler class that redirects to supplied `url`
    """
    class RedirectHandler(http.server.SimpleHTTPRequestHandler):
       def do_GET(self):
           self.send_response(301)
           self.send_header('Location', url)
           self.end_headers()

    return RedirectHandler
           

def main():

    parser = argparse.ArgumentParser(description='HTTP redirect server')

    parser.add_argument('--port', '-p', action="store", type=int, default=80, help='port to listen on')
    parser.add_argument('--ip', '-i', action="store", default="", help='host interface to listen on')
    parser.add_argument('redirect_url', action="store")

    myargs = parser.parse_args()
    
    redirect_url = myargs.redirect_url
    port = myargs.port
    host = myargs.ip

    redirectHandler = redirect_handler_factory(redirect_url)
    
    handler = socketserver.TCPServer((host, port), redirectHandler)
    handler.serve_forever()

if __name__ == "__main__":
    main()
