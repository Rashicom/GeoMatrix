from .models import LandOwnershipRegistry, LandGeography, LandTypeTaxList, TaxInvoice
from datetime import date
from .serializers import TaxInvoiceSerializer

# tax logics

class LandTax:

    def __init__(self, land_instance=None, new_land=False):
        self.land_instance = land_instance
        self.new_land = new_land

    
    def generate_tax_invoice(self):
        """
        this method generates tax invoice for prticlular land
        which is new or not
        return invoice instance if it created else return error response
        """

        # fetching informatin to update database
        land = self.land_instance
        registry_user = LandOwnershipRegistry.objects.filter(land=land).last()
        
        land_geo_instance = LandGeography.objects.get(land=land)
        
        area = land_geo_instance.area
        land_type = land_geo_instance.land_type

        # calculating land tax using land area and land type    
        land_type_tax = LandTypeTaxList.objects.get(land_type=land_type).land_tax

        # land tax = land_type_tax * number of cent
        # 1 sqr meter = 0.024 cent
        number_of_cent = area*0.024
        amount = number_of_cent*land_type_tax
        
        # generate invoice if new land
        if self.new_land:
            # tax invoice amount is for one week
            days = (date.today() - land.active_from).days
            number_of_weeks = days/7
            total_amount = amount*number_of_weeks

        # generate invoice for existed land, in this case inesial date is the last invoice date
        else:
            land_invoice = TaxInvoice.objects.filter(land=land).last()
            days = (date.today() - land_invoice.tax_date).days
            number_of_weeks = days/7
            total_amount = amount*number_of_weeks
            
        # create invoide and return instance 
        try:
            invoice = TaxInvoice.objects.create(
                land=land,
                registry_user=registry_user,
                area=area,
                amount=total_amount
            )
            return invoice
        except Exception as e:
            print(e)
            return {"details":"land creation filed"}
        


