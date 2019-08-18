import http.server
import socketserver
import api
from urllib import parse
import json

PORT = 8001

class ThisServerRequestHandler(http.server.BaseHTTPRequestHandler):
	def __parseServerUrl__(self, url):
		parseData = parse.urlsplit(url)
		query = parseData.query
		parsed = parse.parse_qs(query)
		
		return parsed, parseData
			
	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		
		parsedUrl, parseData = self.__parseServerUrl__(self.path)
		
		apiPath = parseData.path
		
		if apiPath == '/api/':
			portalName = parsedUrl['portal'][0]		
		
			items = api.getItem(portalName)
			self.wfile.write(json.dumps(items).encode("utf-8"))
		else:
			return

Handler = ThisServerRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
	print("serving at port", PORT)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.shutdown()


