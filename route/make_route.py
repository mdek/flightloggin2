from airport.models import Location, HistoricalIdent
from models import RouteBase, Route

class MakeRoute(object):
    """
    creates a route object from a string. The constructor takes a user
    instance because it needs to know which "namespace" to use for
    looking up custom places.
    """
    
    def __init__(self, fallback_string, user, date=None):
        self.user = user
        
        # the date of this route, so we know which identifiers to look for
        self.date = date
       
        if not fallback_string:     #return empty route
            self.route = Route()
            self.route.save()
            return None
        
        route = Route(fallback_string=fallback_string, p2p=False)
        route.save()
        
        is_p2p, routebases = self.make_routebases_from_fallback_string(route)
        
        route.p2p = is_p2p
        
        for routebase in routebases:
            routebase.route = route
            routebase.save()
            
        route.easy_render()
        
        self.route = route
    
    def get_route(self):
        return self.route
    
    ###########################################################
    ###########################################################
   
            
    def normalize(self, string):
        """
        removes all cruf away from the route string, returns only the
        alpha numeric characters with clean seperators
        """
        
        import re
        string = string.upper()
        string = string.replace("LOCAL", " ")
        string = string.replace(" TO ", " ")
        return re.sub(r'[^A-Z0-9!@]+', ' ', string).strip()

    ###########################################################
    ########################################################### 
        
    def find_navaid(self, ident, i, last_rb=None):
        """
        Searches the database for the navaid object according to ident.
        if it finds a match, creates and returns a routebase object
        """
               
        if last_rb:
            navaid = Location.objects.filter(loc_class=2, identifier=ident)
            #if more than 1 navaids come up,
            if navaid.count() > 1:
                #run another query to find the nearest
                last_point = last_rb.location 
                navaid = navaid.distance(last_point.location)\
                               .order_by('distance')[0]
                               
            elif navaid.count() == 0:
                navaid = None
            else:
                navaid = navaid[0]
        else:
            # no previous routebases,
            # dont other with the extra queries trying to find the nearest 
            # based on the last
            navaid = Location.goon(loc_class=2,
                                   identifier=ident)
        if navaid:
            return RouteBase(location=navaid, sequence=i)
        else:
            # wasn't a navaid, maybe it was an airport that they flew over?
            return self.find_airport(ident, i)
        
        return None
        
    ###########################################################################

    def find_custom(self, ident, i, force=False):
        """
        Tries to find the custom point, if it can't find one, and
        force = True, it adds it to the user's custom list.
        """
        
        ident = ident[:8]
        
        if force:
            cu,cr = Location.objects.get_or_create(user=self.user,
                                                  loc_class=3,
                                                  identifier=ident)
        else:
            cu = Location.goon(loc_class=3,
                               user=self.user,
                               identifier=ident)

        if cu:
            return RouteBase(location=cu, sequence=i)
        else:
            return None

    ###########################################################################

    def find_airport(self, ident, i):
        from models import RouteBase
        
        date = self.date
        
        hi = None
        if date:
            #first try to get historical ident
            try:
                hi = HistoricalIdent.goon(identifier__endswith=ident)
            except HistoricalIdent.MultipleObjectsReturned:
                hi = HistoricalIdent.goon(identifier__endswith=ident,
                                          start__lte=date,
                                          end__gte=date)
        
        if hi:              ## XXX remove str() after switching to django 1.2
            airport = Location.goon(loc_class=1, identifier=str(hi.current_location))
        else:
            airport = Location.goon(loc_class=1, identifier=ident)
            
        if not airport and len(ident) == 3:
            # if the ident is 3 letters and no hit, try again with an added 'K'
            airport = Location.goon(loc_class=1,
                                    identifier="K%s" % ident)

        if airport:
            return RouteBase(location=airport, sequence=i)
        
        return None

    def make_routebases_from_fallback_string(self, route):
        """
        Returns a list of RouteBase objects according to the fallback_string,
        basically hard_render()
        """
        
        fbs = self.normalize(route.fallback_string)
        points = fbs.split()     # 'MER / VGA - mer' -> ['MER', 'VGA', 'MER']
        unknown = False
        p2p = []
        routebases = []
        
        for i, ident in enumerate(points):
        
            if "@" in ident:        # "@" means we didn't land
                land = False
            else:
                land = True
                
            if "!" in ident:        # "!" means it's a custom place
                custom = True
            else:
                custom = False
                
            #replace all the control characters now that we know their purpose
            ident = ident.replace('!','').replace('@','')
                
            if not land and not custom:     # must be a navaid
                # is this the first routebase? if so don't try to guess which
                # navaid is closest to the previous point
                
                first_rb = len(routebases) == 0  
                if not first_rb and not routebases[i-1].unknown:
                    routebase = self.find_navaid(ident, i, last_rb=routebases[i-1])
                else:
                    routebase = self.find_navaid(ident, i)
            
            elif custom:
                # force=True means if it can't find the 'custom', then make it
                routebase = self.find_custom(ident, i, force=True)
                
            else:                  #must be an airport  
                routebase = self.find_airport(ident, i)
                if not routebase:
                    # if the airport can't be found, see if theres a 'custom'
                    # by the same identifier
                    routebase = self.find_custom(ident, i, force=False)
                
            #######################################################################
           
            # no routebase? must be unknown
            if not routebase:
                routebase = RouteBase(unknown=ident, sequence=i)
            
            routebase.land = land
            routebases.append(routebase)
            
            if land:
                loc = routebase.location or ident
                p2p.append(loc)

        return len(set(p2p)) > 1, routebases
