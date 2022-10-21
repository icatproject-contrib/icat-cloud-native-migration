from icat_db_generator import post_entity, get_date_time
import models

class DoiMinter:
    def data_publication_type_generator(self, type):
        self.data_publication_type = models.DATAPUBLICATIONTYPE()
        self.data_publication_type.createId = "user"
        self.data_publication_type.modId = "user"
        self.data_publication_type.modTime = get_date_time()
        self.data_publication_type.createTime = get_date_time()
        self.data_publication_type.description = type
        self.data_publication_type.name = type
        self.data_publication_type.facilityID = 1
        post_entity(self.data_publication_type)

    def generate_doiminters_user(self):
        self.user = models.USER()
        self.user.id = 500
        self.user.createId = "user"
        self.user.modId = "user"
        self.user.modTime = get_date_time()
        self.user.createTime = get_date_time()
        self.user.name = "doiminter"
        post_entity(self.user)

    def generate_doiminters_group(self):
        self.grouping = models.GROUPING()
        self.grouping.id = 30
        self.grouping.createId = "user"
        self.grouping.modId = "user"
        self.grouping.modTime = get_date_time()
        self.grouping.createTime = get_date_time()
        self.grouping.name = "doiminters"
        post_entity(self.grouping)

    def generate_doiminters_user_group(self):
        self.user_group = models.USERGROUP()
        self.user_group.createId = "user"
        self.user_group.modId = "user"
        self.user_group.modTime = get_date_time()
        self.user_group.createTime = get_date_time()
        self.user_group.groupID = 30
        self.user_group.userID = 500
        post_entity(self.user_group)

    def generate_rules(self, what, flags):
        self.rule = models.RULE()
        self.rule.createId = "user"
        self.rule.modId = "user"
        self.rule.modTime = get_date_time()
        self.rule.createTime = get_date_time()
        self.rule.crudFlags = flags
        self.rule.what = what
        self.rule.groupingID = 30
        post_entity(self.rule)

    def add_specific_entries(self):
        self.data_publication_type_generator("User-defined")
        self.data_publication_type_generator("Investigation")
        self.generate_doiminters_user()
        self.generate_doiminters_group()
        self.generate_doiminters_user_group()
        self.generate_rules("Dataset", "CRUD")
        self.generate_rules("DataCollectionDataset", "CRUD")
        self.generate_rules("DataPublicationUser", "CRUD")
        self.generate_rules("Investigation", "R")
        self.generate_rules("Affiliation", "CRUD")
        self.generate_rules("Datafile", "CRUD")
        self.generate_rules("Facility", "R")
        self.generate_rules("User", "R")
        self.generate_rules("DataCollectionDatafile", "CRUD")
        self.generate_rules("InvestigationUser", "R")
        self.generate_rules("DataCollection", "CRUD")
        self.generate_rules("DataPublicationType", "R")
        self.generate_rules("DataPublicationDate", "CRUD")
        self.generate_rules("DataCollectionInvestigation", "CRUD")
        self.generate_rules("DataPublication", "CRUD")



