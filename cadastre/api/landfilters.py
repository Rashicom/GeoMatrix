from datetime import date
from .models import Land
from django.db.models import Q

# active / non active lands filtesr
# district  locality state filter
# land type filter
# lands inside a large poligon filter(role based admin land retruve)

# timestamp filter to see changes over time

def date_stamp_filter(date=date.today):
    
    date_filter = Q(active_from__lt=date) & Q(active_till__gt=date)
    
    land_list = Land.objects.filter(date_filter)
    return land_list

