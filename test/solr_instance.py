import subprocess

class SolrInstance(object):
    def __init__(self):
        self._process = None

    def start(self):
        args = [
        'java -Dcollection.configName=myconf -DzkRun -DnumShards=1 -jar start.jar >/dev/null',
            ]

        self._process = subprocess.Popen(args=args,
                                         shell=True,
                                         cwd='/home/dfdeshom/code/solr-4.6.0/example')


    def flush(self):
        pass

    def terminate(self):
        self._process.terminate()
        self._process.wait()
        self._process = None
