from collections import defaultdict

from future.utils import iteritems, iterkeys


class BaseParams(object):
    def __init__(self, query=None, **kwargs):
        """
        :param query: the query to send to solr
        :type query: str
        """
        self._q = defaultdict(set)
        if query:
            self._q["q"].add(query)

        for k, v in list(kwargs.items()):
            if hasattr(v, "__iter__") and not isinstance(v, str):
                self._q[k].update(v)
            else:
                self._q[k].update([v])

    def add_params(self, **kwargs):
        """
        Takes keyword arguments and adds them as key-value pairs to params to be sent to solr
        :return: self
        :rtype: BaseParams
        """
        for k, v in list(kwargs.items()):
            if hasattr(v, "__iter__") and not isinstance(v, str):
                self._q[k].update(v)
            else:
                self._q[k].update([v])
        return self

    def remove_param(self, key):
        """
        Removes a parameter from the request being prepared
        """
        self._q.pop(key, None)

    def __repr__(self):
        """
        :return: str
        :rtype: str
        """
        c = self._q.copy()
        return repr(dict(c))

    def __iter__(self):
        """
        :return: an iterable
        :rtype: iterable
        """
        c = self._q.copy()
        return iter(list(dict(c).items()))

    def __getitem__(self, item):
        """
        Convenience method to allow retrieval from param keys
        :param item: the key
        :type item: str
        :return: the value stored under that key
        """
        return self._q[item]

    def iterkeys(self):
        """
        :return: an iterable
        :rtype: iterable
        """
        return iterkeys(self._q)

    def __len__(self):
        """
        :return: size of the params
        :rtype: int
        """
        return len(self._q)


class CommonParams(BaseParams):

    """
    Common parameters passed to search queries. These parameters
    are usually found under Solr's `/select` handler
    """

    def q(self, query):
        """
        Adds query parameter
        :param query: the query to be sent to solr
        :type query: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["q"].add(query)
        return self

    def sort(self, criteria):
        """
        Adds sort parameter
        :param criteria: the sort directive to be sent to solr
        :type criteria: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["sort"].add(criteria)
        return self

    def start(self, start):
        """
        Adds start parameter to solr request
        :param start: starting result offset to be requested from solr
        :type start: int
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["start"].add(start)
        return self

    def rows(self, r):
        """
        Adds start parameter to solr request
        :param start: starting result offset to be requested from solr
        :type start: int
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["rows"].add(r)
        return self

    def fq(self, query):
        """
        Adds filter query parameter to solr request
        :param fq: filter query
        :type fq: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["fq"].add(query)
        return self

    def fl(self, fields):
        """
        Adds field parameter to solr request
        :param fields: comma-separated field names
        :type fields: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["fl"].add(fields)
        return self

    def deftype(self, t):
        """
        Allows specification of parser during request handling
        :param t: a string name of parser type, e.g. lucene, edismax
        :type t: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["defType"].add(t)
        return self

    def explain_other(self, val):
        """
        Asks Solr to explain how documents matching a particular query were graded against the query used
        :param val: a query string
        :type val: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["explainOther"].add(val)
        return self

    def time_allowed(self, t):
        """
        Add timeout to search
        :param t: a timeout value
        :type t: int
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["timeAllowed"].add(t)
        return self

    def cache(self, val):
        """
        Allows definition of caching of filters, causes filtering to be done at the same time as search
        :param val: true or false string
        :type val: str
        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["cache"].add(val)
        return self

    def log_param_list(self, val):
        """
        This isn't in Solr's documentation...
        """
        self._q["logParamList"].add(val)
        return self

    def debug(self):
        """
        Enables debugging for a particular query

        :return: self for fluent interface
        :rtype: CommonParams
        """
        self._q["debug"].add("true")
        return self


class MLTParams(BaseParams):

    """
    Parameters passed to mlt searches
    """

    def fl(self, field):
        """
        Adds field parameter to solr mlt request
        :param field: comma-separated field names
        :type field: str
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.fl"].add(field)
        return self

    def mintf(self, tf):
        """
        Adds minimum term frequency parameter to solr mlt request
        :param tf: the minimum term frequency
        :type tf: float
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.mintf"].add(tf)
        return self

    def mindf(self, df):
        """
        Adds minimum document frequency parameter to solr mlt request
        :param df: the minimum document frequency
        :type df: float
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.mindf"].add(df)
        return self

    def minwl(self, wl):
        """
        Adds minimum word length parameter to solr mlt request
        :param wl: the minimum word length
        :type wl: int
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.minwl"].add(wl)
        return self

    def maxwl(self, wl):
        """
        Adds maximum word length parameter to solr mlt request
        :param wl: the maximum word length
        :type wl: int
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.maxwl"].add(wl)
        return self

    def maxqt(self, qt):
        """
        Adds maximum query terms parameter to solr mlt request
        :param qt: the maximum query terms
        :type qt: int
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.maxqt"].add(qt)
        return self

    def maxntp(self, ntp):
        """
        Adds maximum number of tokens to parse parameter to solr mlt request
        :param ntp: the maximum number of tokens to parse
        :type ntp: int
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.maxntp"].add(ntp)
        return self

    def boost(self, val):
        """
        Sets if the query will be boosted by the interesting term service
        :param val: a string boolean (lowercase)
        :type val: str
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.boost"].add(val)
        return self

    def qf(self, fields):
        """
        Specifies the query fields
        :param fields: a string of comma-separated fields
        :type fields: str
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.qf"].add(fields)
        return self

    def count(self, c):
        """
        Number of similar documents to return for each result
        :param c: the number of similar documents desired
        :type c: int
        :return: self for fluent interface
        :rtype: MTLParams
        """
        self._q["mlt.count"].add(c)
        return self


class FacetParams(BaseParams):

    """
    Parameters to pass when doing faceted search
    """

    def query(self, query):
        """
        The facet query
        :param query: the query to facet against
        :type query: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.query"].add(query)
        return self

    def field(self, field):
        """
        The facet field
        :param field: the field we want facets for
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.field"].add(field)
        return self

    def prefix(self, criteria, field=None):
        """
        The facet prefix
        :param criteria: the prefix to filter your facets
        :type criteria: str
        :param field: specify a field to prefix against
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.prefix" % field].add(criteria)
        else:
            self._q["facet.prefix"].add(criteria)
        return self

    def sort(self, criteria, field=None):
        """
        The facet prefix
        :param criteria: how to sort facets -- one of "count" or "index"
        :type criteria: str
        :param field: specify a field to sort against
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if criteria not in ["count", "index"]:
            criteria = "count"

        if field:
            self._q["f.%s.facet.sort" % field].add(criteria)
        else:
            self._q["facet.sort"].add(criteria)

        return self

    def limit(self, limit, field=None):
        """
        Limit the number of facet results
        :param limit: the number of results
        :type limit: int
        :param field: specify a field to limit against
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.limit" % field].add(limit)
        else:
            self._q["facet.limit"].add(limit)
        return self

    def offset(self, offset, field=None):
        """
        Facet result offset
        :param offset: the result offset
        :type offset: int
        :param field: specify a field to offset against
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.offset" % field].add(offset)
        else:
            self._q["facet.offset"].add(offset)
        return self

    def mincount(self, count, field=None):
        """
        Specify a minimum number of results required
        :param count: the facet result minimum
        :type count: int
        :param field: specify a field to apply filter against
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.mincount" % field].add(count)
        else:
            self._q["facet.mincount"].add(count)
        return self

    def missing(self, val, field=None):
        """
        Whether to include values missing from facet query
        :param val: a boolean string
        :type val: str
        :param field: specify a field to apply this to
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.missing" % field].add(val)
        else:
            self._q["facet.missing"].add(val)
        return self

    def method(self, m, field=None):
        """
        Which faceting method to use
        :param m: the facet method, one of ['enum', 'fc', 'fcs']
        :type m: str
        :param field: specify a field to apply this to
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.method" % field].add(m)
        else:
            self._q["facet.method"].add(m)
        return self

    def mindf(self, val, field=None):
        """
        Adds minimum document frequency parameter to solr mlt request
        :param val: the minimum document frequency
        :type val: float
        :param field: specify a field to apply this to
        :type field: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        if field:
            self._q["f.%s.facet.enum.cache.minDf" % field].add(val)
        else:
            self._q["facet.enum.cache.minDf"].add(val)
        return self

    def threads(self, num):
        """
        Number of threads to use for this facet request
        :param num: the number of threads
        :type num: int
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.threads"].add(num)
        return self

    def range(self, field, start, end, gap):
        """
        Allows us to specify facet ranges for a given field
        :param field: the field
        :type field: str
        :param start: the starting offset
        :type start: int
        :param end: where the facet range ends
        :type end: int
        :param gap: the gap of each faceted range
        :type gap: int
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.range"].add(field)
        self._q["f.%s.facet.range.start" % field].add(start)
        self._q["f.%s.facet.range.end" % field].add(end)
        self._q["f.%s.facet.range.gap" % field].add(gap)
        return self

    def pivot(self, fields):
        """
        Allow for decision-tree faceting
        :param fields: a comma-separated list of fields to pivot against
        :type fields: str
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.pivot"].add(fields)
        return self

    def pivot_mincount(self, count):
        """
        Specify the minimum number of results in a given pivot
        :param count: the minimum number
        :type count: int
        :return: self for fluent interface
        :rtype: FacetParams
        """
        self._q["facet.pivot.mincount"].add(count)
        return self


class SearchOptions(object):

    """
    Manage options to pass to a solr query

    Although one can use plain dictionaries to pass parameters to solr, this class
    makes this task more convenient. Currently, it covers all options to pass to do:

     - MLT search via the `mltparams`  member variable
     - normal search via `commonparams` member variable
     - faceted search via the `facetparams` member variable

    Example:

        >>> se = SearchOptions()
        >>> se.commonparams.q("*:*").fl('*,score')
        {'q': set(['*:*']), 'fl': set(['*,score'])}
        >>> se.facetparams.field("id")
        {'facet.field': set(['id'])}
        >>> se
        {'commonparams': {'q': set(['*:*']), 'fl': set(['*,score'])}, 'facetparams': {'facet.field': set(['id'])}, 'mltparams': {}}
    """

    def __init__(self, **kwargs):
        self.commonparams = CommonParams(**kwargs)
        self.facetparams = FacetParams()
        self.mltparams = MLTParams()
        self._all = [
            self.commonparams,
            self.facetparams,
            self.mltparams,
        ]

    def iteritems(self):
        res = defaultdict(set)
        if len(self.facetparams) > 0:
            res.update({"facet": "true"})
        for p in self._all:
            res.update(iter(p))
        return iteritems(res)

    def iterkeys(self):
        res = []
        for p in self._all:
            res += list(iterkeys(p))
        return iter(res)

    def __repr__(self):
        res = dict([(c.__class__.__name__.lower(), c) for c in self._all])
        return repr(res)
