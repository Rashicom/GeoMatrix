from datetime import date
from .models import Land
from django.db.models import Q

# active / non active lands filtesr
# district  locality state filter
# land type filter
# lands inside a large poligon filter(role based admin land retruve)



class BaseLandFilters:

    def __init__(self):
        self.land_query_set = Land.objects.order_by("land_number")
        

    # time layer filtering
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
    

    # land address filtering
    def land_in_address(self,locality=None, district=None, state=None, zip_code=None, land_set=None, active_land_only=True):
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

        # after filtering if filtered data not exist we cond want to let it pass through active alnd only check
        # if it , it call active_land function land_set = none in this case, method grab all data from land record and couse a returning all land files
        if len(filtered_data) == 0:
            return filtered_data
        
        # return data according to the active_land_only value
        # if active_land_only is true
        # DEFAULT: True
        if active_land_only:
            return self.active_land(land_set=filtered_data)

        # if user set active_land_only=False return all data
        else:
            
            return filtered_data
    

    # land type filter
    def land_type_filter(self, land_set=None, land_type_list=list()):
        """
        accept: land_type <list>
        return: <QuerySet>
        filtering the land table according to the given list
        """

        # if land set is given perform operation on it. else land_set set to full land data set
        land_set = land_set if land_set else self.land_query_set
        
        # filtering using the land_type_list(revers relational lookup)
        filtered_data = land_set.filter(land_geography__land_type__in=land_type_list)

        return filtered_data



    # active land filtering
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
