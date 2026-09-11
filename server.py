import http.server, socketserver, json, os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from src.agent.models import CustomerMessage
from src.agent.agent_pipeline import ProductionSupportAgent

PORT = int(os.environ.get('PORT', 8000))
agent = ProductionSupportAgent()

class SupportAgentHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            if os.path.exists('static/index.html'):
                with open('static/index.html', 'rb') as hf:
                    self.wfile.write(hf.read())
            else:
                self.wfile.write(b'<h1>Apple Support AI Agent; web Demo</h1>')
        elif self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "agent": "AppleSupportAgent"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/process':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode('utf-8'))
                text = payload.get('text', '')
                msg = CustomerMessage(id='live_query', text=text)
                output = agent.process(msg)
                response_bytes = json.dumps(output.to_dict()).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(('0.0.0.0', PORT), SupportAgentHandler) as httpd:
        print(f'Apple Support AI Agent Server listening on port {PORT}...')
        httpd.serve_forever()
