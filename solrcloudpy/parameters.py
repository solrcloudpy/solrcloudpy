from collections import defaultdict

class Params(object):
    def __init__(self, query=None, *args, **kwargs):
        self._q = defaultdict(set)
        extraparams = {'wt':'json',
                       'omitHeader':'true',
                       'json.nl':'map'}
        kwargs.update(extraparams)
        if query:
            self._q['q'].add(query)

        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self._q[k].update(v)
            else:
                self._q[k].update([v])
        
    def query(self,query):
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

    def fields(self,fields):
        self._q['fl'].add(fields)
        return self

    def debug(self):
        self._q['debug'].add("true")
        return self

    def add_params(self,**kwargs):
        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self._q[k].update(v)
            else:
                self._q[k].update([v])
        return self

    def __repr__(self):
        return repr(dict(self._q))

    def __iter__(self):
        return self._q.iteritems()

    @property
    def facet(self):
        return FacetParams(**self._q)

    @property
    def mlt(self):
        return MLTParams(**self._q)

class MLTParams(Params):
    def __init__(self, *args, **kwargs):
        super(MLTParams,self).__init__(*args,**kwargs)

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


class FacetParams(Params):
    def __init__(self, *args, **kwargs):
        super(FacetParams,self).__init__(*args,**kwargs)
        self._q['facet'].add('true')

    def facet_query(self,query):
        self._q['facet.query'].add(query)
        return self

    def facet_field(self,field):
        self._q['facet.field'].add(field)
        return self

    def prefix(self,criteria,field=None):
        if field:
            self._q['f.%s.facet.prefix'%field].add(criteria)
        else:
            self._q['facet.prefix'].add(criteria)
        return self

    def facet_sort(self,criteria,field=None):
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
