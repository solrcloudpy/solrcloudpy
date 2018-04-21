from __future__ import print_function
from future.moves.urllib.request import urlopen
import subprocess
import time
import os
import re


class SolrInstance(object):
    def __init__(self, name):
        """
        :param name: the name of the collection
        :type name: str
        """

        self._process = None
        self.name = name
        # e.g. /home/dfdeshom/code/solr-4.6.0/
        self.solr_dir = os.getenv('SOLR_HOME', None)
        if not self.solr_dir:
            return

        self.solr_jar_dir = self.solr_dir + '/server'
        self.zoo_data_2 = self.solr_dir + '/example/cloud/node1/solr/zoo_data/version-2/'
        self.collection2_data = self.solr_dir + '/example/cloud/node2'
        self.conf_dir = self.solr_jar_dir + '/solr/configsets/data_driven_schema_configs/conf'

        if self.solr_dir:
            # find the solr version
            with open(self.solr_dir+'/CHANGES.txt', 'r') as changes_file:
                for line in changes_file:
                    if '====' in line:
                        matches = re.match(r'.*(\d+)\.(\d+)\.(\d+).*', line)
                        self.solr_semver = [int(x) for x in matches.groups()]
                        break

            if self.solr_semver[0] == 4:
                self.solr_jar_dir = self.solr_dir+'/example'
                self.zoo_data_2 = self.solr_jar_dir + '/solr/zoo_data/version-2/'
                self.collection2_data = self.solr_jar_dir + '/solr/coll2*'
                self.conf_dir = self.solr_jar_dir+'/solr/collection1/conf'

    def start(self):
        if self.solr_dir:
            if self.solr_semver[0] == 4:
                subprocess.Popen(['rm -rf %s' % self.zoo_data_2], shell=True)
                subprocess.Popen(['rm -rf %s' % self.collection2_data], shell=True)
                args = [' '.join([
                    'java',
                    '-Dcollection.configName=myconf',
                    '-Dbootstrap_confdir=%s' % self.conf_dir,
                    '-DzkRun',
                    '-DnumShards=1',
                    '-jar',
                    'start.jar>/dev/null'
                ])]
                self._process = subprocess.Popen(args=args,
                                                 shell=True,
                                                 cwd=self.solr_jar_dir)
            else:
                args = ['./bin/solr start -e cloud -noprompt']
                self._process = subprocess.Popen(args=args,
                                                 shell=True,
                                                 cwd=self.solr_dir)

    def wait_ready(self):
        if not self._process or self.solr_semver[0] == 4:
            sleeper = 0
            while True:
                try:
                    res = urlopen("http://localhost:8983").read()
                    if res:
                        return True
                except:
                    time.sleep(1)
                    sleeper += 1
                    if sleeper > 15:
                        raise Exception("Waited 15 seconds and no solr to be had -- please check your solr distro")
        else:
            self._process.wait()
            return True

    def flush(self):
        pass

    def terminate(self):
        if self.solr_dir:
            if self.solr_semver[0] == 4:
                # this is too damn broad
                subprocess.Popen(args=['killall -9 java'], shell=True)
            else:
                args = ['./bin/solr stop -all']
                self._process = subprocess.Popen(args=args,
                                                 shell=True,
                                                 cwd=self.solr_dir).wait()

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'start':
        print("Starting Solr")
        instance = SolrInstance('solr2')
        instance.start()
        instance.wait_ready()
        print("Started Solr")
        sys.exit(0)
    if sys.argv[1] == 'stop':
        SolrInstance('solr2').terminate()
        print("Terminated Solr")
        sys.exit(0)
