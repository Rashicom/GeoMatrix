
from .models import Gov_body_Address

# additioal functons are listed here

"""///////////////// NORMAL USERS ////////////////////"""







"""///////////////// GOV USER ////////////////////"""

# checking user have a unique role on a state
# one state cannot have a multiple state role gov_users
class UniqueGovUser:

    def __init__(self,*args, **kwargs):
        """
        all the fields are fetched when an object is created
        """
        self.role = kwargs.get("role")
        self.state = kwargs.get("state")
        self.district = kwargs.get("district")
        self.locality = kwargs.get("locality")        


    # checking any gov user already registered on the target place
    def is_unique(self):
        """
        this function is checking the role and call appropriate fuction check
        each fuction return boorean value corresponding to, is any gov user already registered for that target location or not

        why i checked in this wahy ?

        for each role we have to check:
        STATE: check is there any other user in the same role for same state
        DISTRICT: check is there any other user in the same role for same state, district
        LOCAITY: check is there any other user in the same role for same state, district and locality

        becouse multiple state and district which contains the same named locality and district
        eg:
        address 1: kerala malappuram thuvvur    
        address 2: kerala eranakulam thuvvur
        address 3: thamilnadu malappuram vinnoor

        for state we are checking, is there any other government user with role STATE registered for that perticular state
        we dont want to check the other address fiels like district and locality.

        for district we are checking, is there any other government user with role DISTRICT registered for that perticular district
        in this case we have to check the state and district

        for locality we are checking, is there any other government user with role LOCALITY registered for that perticular LOCALITY
        in this case we have to check Bothe state,district and locality, becouse may be there are multiple district or state contains smae named locality or state
        """

        # first checking the role is provided or not.
        # role is requered for further checking
        if self.role is None:
            raise Exception("Role is not found")

        # if the role is STATE, checking is any other gov_user already registered for the same state as a STATE role
        if self.role == "STATE":
            return self.is_unique_state()
        
        # if the role is DISTRICT, checking is any other gov_user already registered for the same sistrict as a DISTRICT role
        elif self.role == "DISTRICT":
            return self.is_unique_district()
        
        # if the role is LOCAL, checking is any other gov_user already registered for the same locality as a LOCAL role
        elif self.role == "LOCAL":
            return self.is_unique_locality()


    # checking any state role user for the perticular state
    def is_unique_state(self):
        """
        checking in the data base for registered gov_user for the same state
        returs a boolean response
        """

        # state is required to check
        if self.state is None:
            print("exception found")
            raise Exception("addess field incomplete")

        if Gov_body_Address.objects.filter(state=self.state, gov_body__role=self.role).exists():
            return False
        else:
            return True


    # checking any district role user for the perticular distric
    def is_unique_district(self):
        """
        checking in the data base for registered gov_user for the same district
        returs a boolean response
        """

        # state and district is required to check
        if self.state is None or self.district is None:
            raise Exception("addess field incomplete")

        if Gov_body_Address.objects.filter(state=self.state, district=self.district, gov_body__role=self.role).exists():
            return False
        else:
            return True
    

    # checking any local role user for the perticular locality
    def is_unique_locality(self):
        """
        checking in the data base for registered gov_user for the same locality
        returs a boolean response
        """

        # state,district and locality is required to check
        if self.state is None or self.district is None or self.locality is None:
            raise Exception("addess field incomplete")

        if Gov_body_Address.objects.filter(state=self.state, district=self.district, locality=self.locality, gov_body__role=self.role).exists():
            return False
        else:
            return True
    
    
        


