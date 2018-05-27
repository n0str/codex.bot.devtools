import subprocess
import requests
import json
import os
from threading import Thread
import yaml
from time import sleep


path = os.path.dirname(os.path.realpath(__file__))


class Ngrok(Thread):

    def __init__(self, port):
        self.stdout = None
        self.stderr = None
        self.port = port
        Thread.__init__(self)

    def run(self):
        p = subprocess.Popen([path + '/ngrok', 'http', str(self.port)],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()


class NgrokLoader:

    def __init__(self):
        self.threads = []
        with open(f'{path}/tunnels.yml') as f:
            self.modules = yaml.safe_load(f).get('ports', [])

    def load(self, modules):
        for module in modules:
            if module not in self.modules:
                raise Exception(f"Module {module} not found in {self.modules}")
            self.threads.append(Ngrok(self.modules[module]))
        self.modules = {m: self.modules[m] for m in self.modules if m in modules}
        [t.start() for t in self.threads]
        sleep(3)

    def get_urls(self):
        ports = {str(self.modules[v]): v for v in self.modules}
        commands = []
        for port in range(4040, 4100):
            try:
                res = json.loads(requests.get(f"http://localhost:{port}/api/tunnels", headers={'Content-Type': 'application/json'}).text)
                for tunnel in res['tunnels']:
                    prt = tunnel['config']['addr'].split(':')[-1]
                    if prt in ports:
                        print(f"{ports[prt]} ({tunnel['config']['addr']}) => {tunnel['public_url']}")
                        commands.append((ports[prt], tunnel['config']['addr'], tunnel['public_url']))
                        ports.pop(prt)
                if not len(ports):
                    break

            except Exception as e:
                print(f"Exception: {e}")
        else:
            print("====\nError.")

    def print_helpers(self, commands):
        with open("run_modules.sh", "w") as w:
            w.write("source venv/bin/activate\n")
            for command in commands:
                host, port = command[1].split(':')
                if command[0] == "core":
                    w.write(f"cd core\nscreen -dmS bot_core python main.py --host {host} --port {port}\ncd ..\n")
                else:
                    w.write(f"cd applications/{command[0]}/{command[0]}\nscreen -dmS bot_{command[0]} python main.py --url {command[2]} --port {port} --host {host}\ncd ../../../\n")

    def join(self):
        [t.join() for t in self.threads]


ngrokLoader = NgrokLoader()
ngrokLoader.load(['core', 'github'])
ngrokLoader.get_urls()
ngrokLoader.join()
