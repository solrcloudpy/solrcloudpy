from collections import defaultdict

class BaseParams(object):
    def __init__(self, query=None, *args, **kwargs):
        self._q = defaultdict(set)
        if query:
            self._q['q'].add(query)

        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self._q[k].update(v)
            else:
                self._q[k].update([v])

    def add_params(self,**kwargs):
        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self._q[k].update(v)
            else:
                self._q[k].update([v])
        return self

    def __repr__(self):
        c = self._q.copy()
        return repr(dict(c))

    def __iter__(self):
        c = self._q.copy()
        return c.iteritems()

    def iterkeys(self):
        return self._q.iterkeys()
    
    def __len__(self):
        return len(self._q)

class CommonParams(BaseParams):
    def q(self,query):
        self._q['q'].add(query)
        return self

    def sort(self,criteria):
        self._q['sort'].add(criteria)
        return self

    def start(self,start):
        self._q['start'].add(start)
        return self

    def rows(self,r):
        self._q['rows'].add(r)
        return self

    def fq(self,query):
        self._q['fq'].add(query)
        return self

    def fl(self,fields):
        self._q['fl'].add(fields)
        return self

    def debug(self):
        self._q['debug'].add("true")
        return self

class MLTParams(BaseParams):
    def mlt_fl(self,field):
        self._q['mlt.fl'].add(field)
        return self

    def mlt_mintf(self,tf):
        self._q['mlt.mintf'].add(tf)
        return self

    def mlt_mindf(self,df):
        self._q['mlt.mindf'].add(df)
        return self

    def mlt_minwl(self,wl):
        self._q['mlt.minwl'].add(wl)
        return self

    def mlt_maxwl(self,wl):
        self._q['mlt.maxwl'].add(wl)
        return self

    def mlt_maxqt(self,qt):
        self._q['mlt.maxqt'].add(qt)
        return self

    def mlt_maxntp(self,ntp):
        self._q['mlt.maxntp'].add(ntp)
        return self

    def mlt_boost(self,val):
        self._q['mlt.boost'].add(val)
        return self

    def mlt_qf(self,fields):
        self._q['mlt.qf'].add(fields)
        return self

    def mlt_count(self,c):
        self._q['mlt.count'].add(c)
        return self

class FacetParams(BaseParams):
    def query(self,query):
        self._q['facet.query'].add(query)
        return self

    def field(self,field):
        self._q['facet.field'].add(field)
        return self

    def prefix(self,criteria,field=None):
        if field:
            self._q['f.%s.facet.prefix'%field].add(criteria)
        else:
            self._q['facet.prefix'].add(criteria)
        return self

    def sort(self,criteria,field=None):
        if criteria not in ["count","index"]:
            criteria = "count"

        if field:
            self._q['f.%s.facet.sort'%field].add(criteria)
        else:
            self._q['facet.sort'].add(criteria)

        return self

    def limit(self,limit,field=None):
        if field:
            self._q['f.%s.facet.limit'%field].add(limit)
        else:
            self._q['facet.limit'].add(limit)
        return self

    def offset(self,offset,field=None):
        if field:
            self._q['f.%s.facet.offset'%field].add(offset)
        else:
            self._q['facet.offset'].add(offset)
        return self

    def mincount(self,count,field=None):
        if field:
            self._q['f.%s.facet.mincount'%field].add(count)
        else:
            self._q['facet.offset'].add(count)
        return self

    def missing(self,val,field=None):
        if field:
            self._q['f.%s.facet.missing'%field].add(val)
        else:
            self._q['facet.missing'].add(val)
        return self

    def method(self,m,field=None):
        if field:
            self._q['f.%s.facet.method'%field].add(m)
        else:
            self._q['facet.method'].add(m)
        return self

    def mindf(self,val,field=None):
        if field:
            self._q['f.%s.facet.enum.cache.minDf'%field].add(val)
        else:
            self._q['facet.enum.cache.minDf'].add(val)
        return self

    def threads(self,num):
        self._q['facet.threads'].add(num)
        return self

    def range(self,field,start,end,gap):
        self._q['facet.range'].add(field)
        self._q['f.%s.facet.range.start'%field].add(start)
        self._q['f.%s.facet.range.end'%field].add(end)
        self._q['f.%s.facet.range.gap'%field].add(gap)
        return self

    def pivot(self,fields):
        self._q['facet.pivot'].add(fields)
        return self

    def pivot_mincount(self,count):
        self._q['facet.pivot.mincount'].add(count)
        return self

class SearchOptions(object):
    def __init__(self):
        self.commonparams = CommonParams()
        self.facetparams = FacetParams()
        self.mltparams = MLTParams()
        self._all = [self.commonparams,
                    self.facetparams,
                    self.mltparams,]

    def iteritems(self):
        res = defaultdict(set)
        if len(self.facetparams) > 0:
            res.update({'facet':'true'})
        for p in self._all:
            res.update(iter(p))
        return res.iteritems()

    def iterkeys(self):
        res = []
        for p in self._all:
            res += list(p.iterkeys())
        return res

    def __repr__(self):
        res = {c.__class__.__name__:c for c in self._all}
        return repr(res)
