from collections import defaultdict

class Params(object):
    def __init__(self, query=None, *args, **kwargs):
        self.__q = defaultdict(set)
        extraparams = {'wt':'json',
                       'omitHeader':'true',
                       'json.nl':'map'}
        kwargs.update(extraparams)
        if query:
            self.__q['q'].add(query)

        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self.__q[k].update(v)
            else:
                self.__q[k].update([v])

    def query(self,query):
        self.__q['q'].add(query)
        return self

    def sort(self,criteria):
        self.__q['sort'].add(criteria)
        return self

    def start(self,start):
        self.__q['start'].add(start)
        return self

    def rows(self,r):
        self.__q['rows'].add(r)
        return self

    def fq(self,query):
        self.__q['fq'].add(query)
        return self

    def fields(self,fields):
        self.__q['fl'].add(fields)
        return self

    def debug(self):
        self.__q['debug'].add("true")
        return self

    def add_params(self,**kwargs):
        for k,v in kwargs.items():
            if hasattr(v,"__iter__"):
                self.__q[k].update(v)
            else:
                self.__q[k].update([v])
        return self

    def __repr__(self):
        return repr(dict(self.__q))

    def __iter__(self):
        return self.__q.iteritems()

    @property
    def facet(self):
        return FacetParams(**self.__q)

    @property
    def mlt(self):
        return MLTParams(**self.__q)

class MLTParams(Params):
    def __init__(self, *args, **kwargs):
        super(MLTParams,self).__init__(*args,**kwargs)

    def mlt_fl(self,field):
        self.__q['mlt.fl'].add(field)
        return self

    def mlt_mintf(self,tf):
        self.__q['mlt.mintf'].add(tf)
        return self

    def mlt_mindf(self,df):
        self.__q['mlt.mindf'].add(df)
        return self

    def mlt_minwl(self,wl):
        self.__q['mlt.minwl'].add(wl)
        return self

    def mlt_maxwl(self,wl):
        self.__q['mlt.maxwl'].add(wl)
        return self

    def mlt_maxqt(self,qt):
        self.__q['mlt.maxqt'].add(qt)
        return self

    def mlt_maxntp(self,ntp):
        self.__q['mlt.maxntp'].add(ntp)
        return self

    def mlt_boost(self,val):
        self.__q['mlt.boost'].add(val)
        return self

    def mlt_qf(self,fields):
        self.__q['mlt.qf'].add(fields)
        return self

    def mlt_count(self,c):
        self.__q['mlt.count'].add(c)
        return self


class FacetParams(Params):
    def __init__(self, *args, **kwargs):
        super(FacetParams,self).__init__(*args,**kwargs)
        self.__q['facet'].add('true')

    def facet_query(self,query):
        self.__q['facet.query'].add(query)
        return self

    def facet_field(self,field):
        self.__q['facet.field'].add(field)
        return self

    def prefix(self,criteria,field=None):
        if field:
            self.__q['f.%s.facet.prefix'%field].add(criteria)
        else:
            self.__q['facet.prefix'].add(criteria)
        return self

    def facet_sort(self,criteria,field=None):
        if criteria not in ["count","index"]:
            criteria = "count"

        if field:
            self.__q['f.%s.facet.sort'%field].add(criteria)
        else:
            self.__q['facet.sort'].add(criteria)

        return self

    def limit(self,limit,field=None):
        if field:
            self.__q['f.%s.facet.limit'%field].add(limit)
        else:
            self.__q['facet.limit'].add(limit)
        return self

    def offset(self,offset,field=None):
        if field:
            self.__q['f.%s.facet.offset'%field].add(offset)
        else:
            self.__q['facet.offset'].add(offset)
        return self

    def mincount(self,count,field=None):
        if field:
            self.__q['f.%s.facet.mincount'%field].add(count)
        else:
            self.__q['facet.offset'].add(count)
        return self

    def missing(self,val,field=None):
        if field:
            self.__q['f.%s.facet.missing'%field].add(val)
        else:
            self.__q['facet.missing'].add(val)
        return self

    def method(self,m,field=None):
        if field:
            self.__q['f.%s.facet.method'%field].add(m)
        else:
            self.__q['facet.method'].add(m)
        return self

    def mindf(self,val,field=None):
        if field:
            self.__q['f.%s.facet.enum.cache.minDf'%field].add(val)
        else:
            self.__q['facet.enum.cache.minDf'].add(val)
        return self

    def threads(self,num):
        self.__q['facet.threads'].add(num)
        return self

    def range(self,field,start,end,gap):
        self.__q['facet.range'].add(field)
        self.__q['f.%s.facet.range.start'%field].add(start)
        self.__q['f.%s.facet.range.end'%field].add(end)
        self.__q['f.%s.facet.range.gap'%field].add(gap)
        return self

    def pivot(self,fields):
        self.__q['facet.pivot'].add(fields)
        return self

    def pivot_mincount(self,count):
        self.__q['facet.pivot.mincount'].add(count)
        return self
