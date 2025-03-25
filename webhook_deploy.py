import os
import shutil
from subprocess import Popen, PIPE, run
from http.server import BaseHTTPRequestHandler, HTTPServer

class Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        directory = '/path/to/base/dir/'
        src = 'path/to/source/'
        dest = 'path/to/destination/'

        run(
            '/usr/bin/git pull',
            shell=True, cwd=directory + src,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )

        changed_files = Popen(
            '/usr/bin/git diff --name-only HEAD HEAD~1',
            shell=True,
            cwd=directory + src,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        ).communicate()[0].strip().decode('utf-8').split('\n')

        for file_name in changed_files:
            full_file_name = os.path.join(directory + src, file_name)
            dest_dir_name = os.path.dirname(directory + dest + file_name)

            if os.path.isfile(full_file_name):
                os.makedirs(dest_dir_name, exist_ok=True)
                shutil.copy(full_file_name, dest_dir_name)
            elif os.path.isfile(directory + dest + file_name):
                os.remove(directory + dest + file_name)

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    httpd = HTTPServer(('', 8081), Webhook)
    httpd.serve_forever()
