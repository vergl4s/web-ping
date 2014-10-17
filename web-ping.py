#! /usr/bin/env python
import requests
import socket
import argparse
from urlparse import urlparse
import sys, time





def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', action='store', dest='url', required=True, help='URL to ping')
    parser.add_argument('-i', '--interval', action='store', dest='i', default='5', required=False, help='Interval between pings in seconds')
    args = parser.parse_args()

    url = args.url
    interval = int(args.i)

    port = 80
    hostname = ''

    hostname, port = validateURL(url)

    #Main loop where the action happens
    while True:

        feedback = []

        #Test if port is open
        portIsOpen = tryConnectingToPort(hostname, port)
        
        if not portIsOpen:
            feedback.append('Port is kill')

        #If port is open, we need to attempt the GET request
        if portIsOpen:
            feedback.append('Port open')

            webServerIsListening, webServerResponse = sendGetRequest(url)

            if webServerIsListening:

                # status_code returns 200 if the server sends anything back - even garbage. 
                # which is why we need to inspect the header to see if there is any http comming back to us
                if validateHTTPResponse(webServerResponse):

                    feedback.append('Web server listening - %s' % (webServerResponse.status_code))
                    feedback.append('Time elapsed - %s' % (webServerResponse.request.elapsed))
                else:
                    feedback.append("Response does not look like HTTP")
            
            else:

                feedback.append('Web server is kill')

        print feedback

        time.sleep(interval)


def sendGetRequest(url):

    #Returns 2 variables if successful - boolean and web server response
    #If  the request fails, return only the boolean flag

    try:
        r = requests.get(url, allow_redirects=True)
        return True, r
    except Exception, e:
        print e
        return False
    

def validateHTTPResponse(r):
    
    try:
        #200 includes any service that repply - ssh, ftp, telnet, etc 
        if r.status_code == 200:

            #are the headers really HTTP?
            if r.headers:
                return True
            #response 200 but no HTTP headers - most likely garbage
            else:
                return False
        #response not 200 - server actually responded with something else, so it must be HTTP
        else:
            return True

    except Exception, e:
        raise e


def validateURL(url):
    #Checks if URL is in a good format and extract hostname and port from it
    if not url:
        sys.exit('No URL?')

    try:
        urlComponents = urlparse(url)


        if not urlComponents.hostname or not urlComponents.port:
            sys.exit('Couldnt extract port or hostname from URL')
            
        hostname = urlComponents.hostname
        port = int(urlComponents.port)

        return hostname, port
    except Exception, e:
        raise e


def tryConnectingToPort(hostname, port):
    #Returns flag saying it port is open
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    res =  s.connect_ex((hostname,port))
    s.close()

    if res == 0:
        return True
    else:
        return False


if __name__ == '__main__':
    main()