"""
Task Manager HTTP Server
Plain Python server with manual routing
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys


def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key not in os.environ:
                        os.environ[key] = value


load_env()


def get_server_port():
    """Get server port from environment or use default"""
    return int(os.environ.get('PORT', 8000))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'DB'))
from database import (
    init_database,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
    update_task_status,
    get_dashboard_stats
)
from models import Task


class TaskManagerHandler(BaseHTTPRequestHandler):
    """HTTP request handler with custom routing"""

    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_file_response(self, filepath, content_type):
        """Send file response"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')

    def _get_request_body(self):
        """Get JSON body from request"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        return {}

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if path == '/':
            self._serve_index()

        elif path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()

        elif path == '/api/tasks':
            status = query_params.get('status', [None])[0]
            priority = query_params.get('priority', [None])[0]
            search = query_params.get('search', [None])[0]
            sort = query_params.get('sort', [None])[0]

            tasks = get_all_tasks(status, priority, search, sort)
            self._send_json_response(200, tasks)

        elif path == '/api/dashboard':
            stats = get_dashboard_stats()
            self._send_json_response(200, stats)

        elif path.startswith('/api/tasks/') and path.split('/')[-1].isdigit():
            task_id = int(path.split('/')[-1])
            task = get_task_by_id(task_id)
            if task:
                self._send_json_response(200, task)
            else:
                self._send_json_response(404, {'error': 'Task not found'})

        elif path.startswith('/css/'):
            filename = path.split('/')[-1]
            frontend_path = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'css', filename)
            self._send_file_response(frontend_path, 'text/css')

        elif path.startswith('/js/'):
            filename = path.split('/')[-1]
            frontend_path = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'js', filename)
            self._send_file_response(frontend_path, 'application/javascript')

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/tasks':
            data = self._get_request_body()

            is_valid, errors = Task.validate(data, is_update=False)
            if not is_valid:
                self._send_json_response(400, {'errors': errors})
                return

            task = create_task(
                title=data['title'].strip(),
                description=data.get('description', '').strip(),
                due_date=data['due_date'].strip(),
                status=data.get('status', 'Pending'),
                priority=data.get('priority', 'Medium')
            )

            self._send_json_response(201, task)

        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        """Handle PUT requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/tasks/') and path.split('/')[-1].isdigit():
            task_id = int(path.split('/')[-1])
            existing = get_task_by_id(task_id)

            if not existing:
                self._send_json_response(404, {'error': 'Task not found'})
                return

            data = self._get_request_body()

            is_valid, errors = Task.validate(data, is_update=True)
            if not is_valid:
                self._send_json_response(400, {'errors': errors})
                return

            task = update_task(
                task_id=task_id,
                title=data['title'].strip(),
                description=data.get('description', '').strip(),
                due_date=data['due_date'].strip(),
                status=data.get('status', 'Pending'),
                priority=data.get('priority', 'Medium')
            )

            self._send_json_response(200, task)

        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/tasks/') and path.split('/')[-1].isdigit():
            task_id = int(path.split('/')[-1])
            existing = get_task_by_id(task_id)

            if not existing:
                self._send_json_response(404, {'error': 'Task not found'})
                return

            delete_task(task_id)
            self._send_json_response(200, {'success': True, 'message': 'Task deleted'})

        else:
            self.send_response(404)
            self.end_headers()

    def do_PATCH(self):
        """Handle PATCH requests (status toggle)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/tasks/') and '/status' in path:
            parts = path.split('/')
            if len(parts) >= 4 and parts[-2] == 'status' and parts[-3].isdigit():
                task_id = int(parts[-3])
                existing = get_task_by_id(task_id)

                if not existing:
                    self._send_json_response(404, {'error': 'Task not found'})
                    return

                data = self._get_request_body()
                new_status = data.get('status', '').strip()

                if new_status not in Task.VALID_STATUS:
                    self._send_json_response(400, {'errors': [f'Invalid status: {new_status}']})
                    return

                task = update_task_status(task_id, new_status)
                self._send_json_response(200, task)
                return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _serve_index(self):
        """Serve the main HTML file"""
        index_path = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'index.html')
        self._send_file_response(index_path, 'text/html')

    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=None):
    """Run the HTTP server"""
    if port is None:
        port = get_server_port()
    server_address = ('', port)
    httpd = HTTPServer(server_address, TaskManagerHandler)
    print(f"Task Manager Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()


if __name__ == '__main__':
    init_database()
    run_server()