"""
Utilities to index large volumes of documents in Solr
"""
import logging
from contextlib import contextmanager

log = logging.getLogger("solrcloud")


class SolrBatchAdder(object):
    """
    Provides an abstraction for batching commits to the Solr
    index when processing documents with pysolr.  `SolrBatchAdder` maintains an internal
    "batch" list, and  when it reaches `batch_size`, it will commit the batch to
    Solr.  This allows for overall better performance when committing large numbers of
    documents.
    """

    def __init__(self, solr, batch_size=100, auto_commit=True):
        """
        `batch_size` is 100 by default; different values may yield
        different performance characteristics, and this of course depends upon your average
        document size and Solr schema.  But 100 seems to improve performance
        significantly over single commits.

        :param solr: a `SolrIndex` object representing the solr index to use
        :type solr: SolrIndex

        :param batch_size: the number of documents to commit at a time. The default is 100
        :type batch_size: int

        :param auto_commit: whether to commit after adding each batch of documents
        :type auto_commit: bool
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

        :param doc: the document
        :type doc: dict
        """
        self._append_commit(doc)

    def add_multi(self, docs_iter):
        """
        Iterate through `docs_iter`, appending each document to
        the batch adder, committing mid-way
        if batch_size is reached.

        :param docs_iter: the list of documents to go through
        :type docs_iter: iterable
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
        log.debug(
            "SolrBatchAdder: flushing {batch_len} articles to Solr (auto_commit={auto_commit})".format(
                batch_len=batch_len, auto_commit=auto_commit
            )
        )
        try:
            self.solr.add(self.batch)
        except Exception as e:
            log.exception(
                "Exception encountered when committing batch, falling back on one-by-one commit"
            )
            log.error(e)
            # one by one fall-back
            for item in self.batch:
                try:
                    self.solr.add([item])
                except Exception as e:
                    log.error("Could not add item to solr index")
                    log.exception(str(e))
            if auto_commit:
                self.commit()

        self.batch = list()
        self.batch_len = 0

    def commit(self):
        """Commit the current batch of documents"""
        try:
            self.solr.commit()
        except Exception as e:
            log.warning(
                "SolrBatchAdder timed out when committing, but it's safe to ignore"
            )

    def _append_commit(self, doc):
        """
        Adds a doc with an optional commit
        :param doc: the document we want to send to solr
        :type doc: dict
        """
        if self.batch_len == self.batch_size:
            # flush first, because we are at our batch size
            self.flush()
        self._add_to_batch(doc)

    def _add_to_batch(self, doc):
        """
        Adds a document and tracks it within a batch context

        :param doc: the document to send to solr
        :type doc: dict
        """
        self.batch.append(doc)
        self.batch_len += 1

    def __unicode__(self):
        fmt = "SolrBatchAdder(batch_size={batch_size},  batch_len={batch_len}, solr={solr}"
        return fmt.format(**vars(self))


@contextmanager
def solr_batch_adder(solr, batch_size=2000, auto_commit=False):
    """
    A context manager for adding documents in solr

    :param solr: a `SolrIndex` object representing the solr index to use
    :type solr: SolrIndex

    :param batch_size: the number of documents to commit at a time. The default is 100
    :type batch_size: int

    :param auto_commit: whether to commit after adding each batch of documents
    :type auto_commit: bool
    """
    batcher = SolrBatchAdder(solr, batch_size, auto_commit)
    try:
        yield batcher
    finally:
        log.info("solr_batch_adder: flushing last few items in batch")
        batcher.flush()
