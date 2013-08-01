from requests.exceptions import *
from requests.models import Response
from contextlib import contextmanager

import datetime as dt
import requests
import urlparse
import json

import logging

log = logging.getLogger('solrcloud')
dthandler = lambda obj: obj.isoformat() if isinstance(obj, dt.datetime) else None

class DictObject(object):
  '''The recursive class for building and representing objects with'''
  def __init__(self, obj):
    if not obj:
      return
    
    for k, v in obj.iteritems():
      if isinstance(v, dict):
        setattr(self, k, DictObject(v))
      else:
        setattr(self, k.encode('utf8','ignore'), v)

  def __getitem__(self, val):
    return self.__dict__[val]
  
  def __repr__(self):
    return 'DictObject{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for
      (k, v) in self.__dict__.iteritems()))
    
class SolrResponse(DictObject):
  """ A generic representation of a solr response """
  def __repr__(self):
    if not self.response:
      return "Empty SolrResponse" 
    return super(SolrResponse,self).__repr__()

class SolrException(Exception):
    pass

class SolrIndex(object):
    """ """
    def __init__(self,connection,collection):
        """
        Search for documents inside a collection

        :param connection : a ``Connection`` to the solr server

        :param collection : the ``Collection`` object that will be searched
        """
        self.connection = connection
        self.collection = collection
        self.client = requests.Session()
        
    def __repr__(self):
        return "SolrIndex<%s>" % self.collection
    
    def _send(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        extraparams = {'wt':'json', 'omitHeader':'true','json.nl':'map'}
        params.update(extraparams)
                
        servers = list(self.connection.servers)
        if not servers:
            raise Exception("no live servers found!")
        
        host = servers.pop(0)

        def make_request(host,path):
            fullpath = urlparse.urljoin(host,path)
            try:
                r = self.client.request(method,fullpath,
                                        params=params,
                                        headers=headers,data=body,timeout=10.0)
        
                if r.status_code == requests.codes.ok:
                    response = r.json()
                else:
                    response = r.text
                return response
            except (ConnectionError,Timeout) as e:
                print 'exception: ', e
                if servers:
                    host = servers.pop(0)
                    return make_request(host,path)
       
        result = make_request(host,path)
        return result

    def _update(self,body):
        path = '%s/update/json' % self.collection
        resp = self._send(path,method='POST',params={},body=body)
        if type(resp) != type({}):
            raise SolrException(resp)
        return resp

    def search(self,q,params={}):
        """
        Search the collection

        :param q     : a string representing the query 

        :param params: additional parameters passed in a dictionary
        """
        path = "%s/select" % self.collection
        params['q'] = q
        data = self._send(path,params)
        if type(data) != type({}):
            raise SolrException(data)
        
        return SolrResponse(data)

    def mlt(self,q,params={}):
        """
        Perform a MoreLikeThis search the collection

        :param q     : a string representing the query 

        :param params: additional parameters passed in a dictionary
        """
        path = "%s/mlt" % self.collection
        params['q'] = q
        data = self._send(path,params)
        if type(data) != type({}):
            raise SolrException(data)
        
        return SolrResponse(data)

    def add(self,docs):
        """
        Add a list of document to the collection

        :param docs : a list of documents to add
        """
        message = json.dumps(docs,default=dthandler)
        response = self._update(message)
        return response

    def delete(self,id=None,q=None,commit=True):
        """
        Delete documents in a collection. Deletes occur either by id or by query

        :param id : the id of the document to pass. 

        :param q  : the query matching the set of documents to delete
        """
        if id is None and q is None:
            raise ValueError('You must specify "id" or "q".')
        elif id is not None and q is not None:
            raise ValueError('You many only specify "id" OR "q", not both.')
        elif id is not None:
            m = json.dumps({"delete":{"id":"%s" % id }})
        elif q is not None:
            m = json.dumps({"delete":{"query":"%s" % q }})
            
        response = self._update(m)
        if commit:
            self.commit()
            
    def optimize(self,waitsearcher=True,softcommit=False):
        """
        Optimize a collection for searching

        :param waitsearcher : whether to make the changes to the collection visible or not
                              by opening a new searcher

        :param softcommit   : whether to perform a soft commit when optimizing
        """
        waitsearcher = str(waitsearcher).lower()
        softcommit = str(softcommit).lower()
        params = {'softCommit': softcommit,
                  'waitSearcher': waitsearcher,
                  'optimize': 'true'
                  }
        path = '%s/update' % self.collection
        response = self._send(path,params)

    def commit(self):
        """ Commit changes to a collection """
        response = self._update('{"commit":{}}')
        return response


@contextmanager
def solr_batch_adder(solr, batch_size=2000, auto_commit=False):
    """
    A context manager for adding documents in solr

    :param solr       : a `SolrIndex` object representing the solr index to use

    :param batch_size : the number of documents to commit at a time. The default is 100

    :param auto_commit: whether to commit after adding each batch of documents
    """
    batcher = SolrBatchAdder(solr, batch_size, auto_commit)
    try:
        yield batcher
    finally:
        log.info("solr_batch_adder: flushing last few items in batch")
        batcher.flush()
        if not auto_commit:
            log.info("solr_batch_adder: auto_commit was False, issuing final commit")
            batcher.commit()
            
class SolrBatchAdder(object):
    def __init__(self, solr, batch_size=100, auto_commit=True):
        """Provides an abstraction for batching commits to the Solr
        index when processing documents with pysolr.  `SolrBatchAdder` maintains an internal
        "batch" list, and  when it reaches `batch_size`, it will commit the batch to
        Solr.  This allows for overall better performance when committing large numbers of
        documents.

        `batch_size` is 100 by default; different values may yield
        different performance characteristics, and this of course depends upon your average
        document size and Solr schema.  But 100 seems to improve performance
        significantly over single commits.
        
        :param solr       : a `SolrIndex` object representing the solr index to use

        :param batch_size : the number of documents to commit at a time. The default is 100

        :param auto_commit: whether to commit after adding each batch of documents
        """
        self.solr = solr
        self.batch = list()
        self.batch_len = 0
        self.batch_size = batch_size
        self.auto_commit = auto_commit

    def add_one(self, doc):
        """
        Add a single document to the batch adder, committing only
        if we've reached batch_size.

        :param doc : the document
        """
        self._append_commit(doc)

    def add_multi(self, docs_iter):
        """
        Iterate through `docs_iter`, appending each document to
        the batch adder, committing mid-way
        if batch_size is reached.

        :param docs_iter: the list of documents to go through
        """
        assert hasattr(docs_iter, "__iter__"), "docs_iter must be iterable"
        for doc in docs_iter:
            self._append_commit(doc)

    def flush(self):
        """
        Flush the batch queue of the batch adder; necessary after 
        successive calls to `add_one` or `add_multi`.
        """
        batch_len = len(self.batch)
        auto_commit = self.auto_commit
        log.debug("SolrBatchAdder: flushing {batch_len} articles to Solr (auto_commit={auto_commit})".format(
            batch_len=batch_len, auto_commit=auto_commit))
        try:
            self.solr.add(self.batch)
        except Exception as e:
            log.exception("Exception encountered when committing batch, falling back on one-by-one commit")
            print "Exception encountered when committing batch, falling back on one-by-one commit"
            print e
            # one by one fall-back
            for item in self.batch:
                try:
                    self.solr.add([item])
                except Exception as e:
                    log.error(u"Could not add item to solr index")
                    log.exception(str(e))
            if auto_commit:
                self.commit()

        self.batch = list()
        self.batch_len = 0

    def commit(self):
        """Commit the current batch of documents """
        try:
            self.solr.commit()
        except :
            log.warning("SolrBatchAdder timed out when committing, but   it's safe to ignore")

    def _append_commit(self, doc):
        if self.batch_len == self.batch_size:
            # flush first, because we are at our batch size
            self.flush()
        self._add_to_batch(doc)

    def _add_to_batch(self, doc):
        self.batch.append(doc)
        self.batch_len += 1

    def __unicode__(self):
        fmt = "SolrBatchAdder(batch_size={batch_size},  batch_len={batch_len}, solr={solr}"
        return fmt.format(**vars(self))
    
   
