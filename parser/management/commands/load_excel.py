# importing required libraries
import os
import pandas as pd

from django.db import transaction
from django.core.management.base import BaseCommand

from parser import models as parser_models


# column model map describing mappiing from columns to db tables
column_model_map = {
    "Name" : "Product.name",
    "P_Type" : "ProductType.p_type",
    "Price" : "Product.price",
    "Quantity" : "Product.quantity",
    "Created_Date" : "Product.created_date",
    "Vendor_Name" : "Vendor.name",
    "Vendor_Address" : "Vendor.address",
}


"""
    model relationship map describing relationship in the models
    Insert Models without relations at beginning
    Insert Relationship Dependencies of Models before the Models in the map 
"""
model_relationship_map = {
    "Vendor": None,
    "ProductType": ["vendor.Vendor"],
    "Product": ["p_type.ProductType"],
}


def log_created(context, object, is_created):
    """Logs Output if Object is Created"""
    if is_created:
        print(f"{context} - {object} Created")


@transaction.atomic
def migrate_data(excel_file):
    """Function to populate db from excel file"""
    try:
        # storing data from excel file as pandas dataframe object
        df = pd.read_excel(excel_file, header=0)
        # iterating through rows in dataframe
        for row in df.itertuples():
            fixtures = {} # empty dictionary to store db model objects
            # extracting data from tables
            for column, model_map in column_model_map.items():
                # extracting data from columns in datafram
                col, model, field = column, *model_map.split('.')
                # getting data of current model from fixture
                model_data = fixtures.get(f"{model}")
                # getting data of column from dataframe
                value = getattr(row, col, None)
                if not model_data:
                    # creating data if not exists
                    fixtures.update({f"{model}": {f"{field}": value}})
                else:
                    # adding model data if exists
                    model_data[f"{field}"] = value
            # managing relationship between the models
            for model_name, relation_map in model_relationship_map.items():
                # getting model from relationship map
                object = getattr(parser_models, model_name, None)
                # getting data of model from fixture
                data = fixtures.get(model_name)
                if relation_map:
                    # iterating through relations and creating them
                    for relation in relation_map:
                        # extracting data from relation
                        field, related_model = relation.split('.')
                        # getting related model instance from fixture
                        related_model = fixtures.get(related_model)
                        # adding related model relationship
                        data.update({f"{field}": related_model})
                # creating or getting model
                object, is_created = object.objects.get_or_create(**data)
                log_created(f"{model_name}", object, is_created)
                # updating fixture with model instance after creation
                fixtures[f"{model_name}"] = object
    except Exception as E:
        raise E


class Command(BaseCommand):
    help = 'Loads data from Excel Sheet into DB'
    
    def handle(self, *args, **options):
        # asking for file from user
        self.stdout.write(self.style.SUCCESS("\nPlease enter excel file path or skip for default"))
        excel_file = input("file_path: ")
        # path of default excel file
        excel_file = "parser/Inventory.xlsx" if not excel_file else excel_file
        if not os.path.exists(excel_file):
            # exiting if user given file does not exists
            self.stdout.write(self.style.ERROR(f"File does not Exists"))
            return
        try:
            migrate_data(excel_file)
            self.stdout.write(self.style.SUCCESS(f"Inserted Data into DB Successfully"))
        except Exception as err:
            self.stdout.write(self.style.ERROR(err))