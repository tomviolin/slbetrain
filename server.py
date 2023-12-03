#!/usr/bin/env python3
import http.server, ssl

from ssl import SSLContext

server_address = ('0.0.0.0', 4443)
httpd = http.server.HTTPServer(server_address, http.server.CGIHTTPRequestHandler)

context = SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('./ssl/certs/apache-selfsigned.crt', './ssl/private/apache-selfsigned.key')

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

httpd.serve_forever()
