from datetime import date
from .models import Land
from django.db.models import Q

# active / non active lands filtesr
# district  locality state filter
# land type filter
# lands inside a large poligon filter(role based admin land retruve)

# timestamp filter to see changes over time


class BaseLandFilters:

    def __init__(self):
        self.land_query_set = Land.objects.order_by("land_number")
        

    def timelayer_snapshort(self, snapshort_date=None, land_set=None):
        """
        this function recieves snashort date a specific time which we want to take
        the time layered data. (see the changes of land spliting and registration)
        this method searching for land those land exist in the specific time period
        searching for time layer date less than active till and grater than active from

        accept: snapshort_date, land_set
        return: filtered land objects <QuerySet>

        if landset passed. the operatin performed on that set
        else operatin performed in full land set
        """

        # if land set is given perform operation on it. else land_set set to full land data set
        land_set = land_set if land_set else self.land_query_set

        # complex q for lands which is active in the period of time_layer
        # snap short time must be in between active from and active till. if active till is null , we take that land too becouse it still active now
        date_filter = Q(active_from__lt=snapshort_date) & (Q(active_till__gt=snapshort_date) | Q(active_till=None))
        
        # filtering time layer snapshort from land_set data
        filtered_data = land_set.filter(date_filter)
        
        return filtered_data
    
    def land_in_address(self,locality=None, district=None, state=None, zip_code=None, land_set=None):
        """
        accept : locality,district,state,zip_code, land_set  default = None
        return filtered data <QuerySet>

        if landset passed. the operatin performed on that set
        else operatin performed in full land set.
        searching lands in the given address and return
        """

        # if land set is given perform operation on it. else land_set set to full land data set
        land_set = land_set if land_set else self.land_query_set
        
        # set all data to filtered set
        filtered_data = land_set

        # then filtered set passing through all address layers
        if state:
            filtered_data = filtered_data.filter(state__iexact=state)
        if district:
            filtered_data =  filtered_data.filter(district__iexact=district)
        if locality:
            filtered_data = filtered_data.filter(locality__iexact=locality)
        if zip_code:
            filtered_data = filtered_data.filter(zip_code=zip_code)
        
        return filtered_data
    
        

    def active_land(self, land_set=None):
        """
        return active land sets

        if landset passed. the operatin performed on that set
        else operatin performed in full land set
        """

        # if land set is given perform operation on it. else land_set set to full land data set
        land_set = land_set if land_set else self.land_query_set

        # return active lands in the privided set
        filtered_data = land_set.filter(is_active=True)
        return filtered_data
