import subprocess
import atexit
import time
import urllib

running_instances = {} # keep track of what we've got

class SolrInstance(object):
    def __init__(self,name):
        self._process = None
        self.name = name
        running_instances[self.name] = self

    def start(self):
        subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/zoo_data/version-2/'],shell=True)
        subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/coll2*'],shell=True)

        args = [
        'java -Dcollection.configName=myconf -Dbootstrap_confdir=./solr/collection1/conf -DzkRun -DnumShards=1 -jar start.jar',
            ]

        self._process = subprocess.Popen(args=args,
                                         shell=True,
                                         cwd='/home/dfdeshom/code/solr-4.6.0/example')

    def wait_ready(self):
        while True:
            try:
                res = urllib.urlopen("http://localhost:8983").read()
                if res:
                    return True
            except:
                time.sleep(1)

    def flush(self):
        pass

    def terminate(self):
        self._process.terminate()
        self._process.wait()
        self._process = None

def _cleanup():
    """Stop all"""
    global running_instances
    for instance in list(running_instances.values()):
        try:
            instance.terminate()
        except:
            pass
    running_instances = {}

def _remove_all():
    subprocess.Popen(['killall -9 java'],shell=True)
    subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/zoo_data/version-2/'],shell=True)
    subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/coll2*'],shell=True)

atexit.register(_cleanup)
atexit.register(_remove_all)
