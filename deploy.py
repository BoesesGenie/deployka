import os
import shutil
from subprocess import Popen, PIPE, run
from http.server import BaseHTTPRequestHandler, HTTPServer
from lib.config_reader import read_config

class Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        directory, src, dest, exclude_dir = read_config().values()

        run(
            '/usr/bin/git pull',
            shell=True,
            cwd=directory + src,
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

        changed_files = [file for file in changed_files if not file.startswith(exclude_dir)]

        for file_name in changed_files:
            full_file_name = os.path.join(directory + src, file_name)
            dest_dir_name = os.path.dirname(directory + dest + file_name)

            if os.path.isfile(full_file_name):
                os.makedirs(dest_dir_name, exist_ok=True)
                shutil.copy(full_file_name, dest_dir_name)
            elif os.path.isfile(directory + dest + file_name):
                os.remove(directory + dest + file_name)

        run('systemctl restart robinhood', shell=True)

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    httpd = HTTPServer(('', 8081), Webhook)
    httpd.serve_forever()
