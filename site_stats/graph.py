from collections import deque

from graphs.linegraph import ProgressGraph, Plot
from models import StatDB
from constants import STATS_TITLES
from django.db.models import Max

class StatsGraph(ProgressGraph):

    def output(self):
        ret = super(StatsGraph, self).output()
        
        title = STATS_TITLES[self.title][0]
        #unit = STATS_TITLES[self.title][1]
        
        #print title
        
        self.set_title(title)
        
        return ret

class SiteStatsPlot(Plot):
    
    def __init__(self, val, rate=False, **kwargs):

        val = str(val)
        
        #exclude zero values (before the routine recorded any data)
        kwarg = {val: 0}
        qs = StatDB.objects.exclude(**kwarg).order_by('dt') 
                                    
        if val.endswith("_7_days"):
            ## filter queryset to only show one data point per day
            ## this is because the 7 days graphs data is only precise to the
            ## day. Below the queryset is limited to only items that are
            ## taken at the 9 PM data poll.
            qs = qs.extra(where=['EXTRACT (HOUR FROM dt) = 18'])
        
        qs = qs.annotate(date=Max('dt'), value=Max(val))\
               .values('date', 'value')
        
        data = list(qs)
 
        self.start = data[0]['date']
        self.end = data[-1]['date']
        
        self.interval_start = self.start # no need to use a pre-interval
        
        super(SiteStatsPlot, self).__init__(data, rate, **kwargs)
        
    def moving_value(self, iterable):
        """
        Calculate the moving total with a deque
        slightly modified because
        """
        
        d = deque([], self.interval)
        
        data = []
        for elem in iterable:
            d.append(elem)
            data.append((abs(sum(d)-elem*len(d)) / len(d)) * self.interval)
            
        return data

    
    
#auv, avg_duration, avg_per_active, day_wmh, day_wmu, dt, id, most_common_manu,
#most_common_tail, most_common_type, non_empty_users, num_7_days, pwm_count,
#pwm_hours, route_earths, time_7_days, total_dist, total_hours, total_logged,
#unique_airports, unique_countries, unique_tn, user_7_days, users

