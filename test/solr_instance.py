import subprocess
import time
import urllib

class SolrInstance(object):
    def __init__(self,name):
        self._process = None
        self.name = name

    def start(self):
        subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/zoo_data/version-2/'],shell=True)
        subprocess.Popen(['rm -rf /home/dfdeshom/code/solr-4.6.0/example/solr/coll2*'],shell=True)

        args = [
        'java -Dcollection.configName=myconf -Dbootstrap_confdir=./solr/collection1/conf  -DzkRun -DnumShards=1 -jar start.jar>/dev/null',
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
        subprocess.Popen(args=['killall -9 java'],shell=True)
