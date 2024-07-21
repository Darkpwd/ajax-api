def app(environ, start_response):
    try:
        with open("index.html", "rb") as arq:
            data = arq.read()
    except IOError:
        status = "404 Not Found"
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return [b"File not found"]

    status = "200 OK"
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    return [data]
