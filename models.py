from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary
from database import Base
from sqlalchemy.dialects.mysql import LONGBLOB # Or MEDIUMBLOB

class Company(Base):
    __tablename__= 'company'

    id= Column(Integer, primary_key=True, index=True)
    company_name= Column(String(50), unique=True)


class Product(Base):
    __tablename__= 'product'

    id= Column(Integer, primary_key= True, index=True)
    product_title= Column(String(50)) # PEP 8: lowercase with words separated by underscores
    company_id= Column(Integer, ForeignKey("company.id")) # Added ForeignKey

class Admin(Base):
    __tablename__= 'admin'

    id= Column(Integer, primary_key=True, index=True)
    admin_name= Column(String(50), unique=True)
    company_id= Column(Integer, ForeignKey("company.id")) # Added ForeignKey
    product_id= Column(Integer, ForeignKey("product.id")) # Added ForeignKey

class User(Base):
    __tablename__= 'user'

    id= Column(Integer, primary_key=True, index=True)
    user_name= Column(String(50), unique=True)
    product_id= Column(Integer, ForeignKey("product.id")) # Added ForeignKey

class File(Base):
    __tablename__= 'file'

    id= Column(Integer, primary_key=True, index=True)
    file_name= Column(String(50), unique=True)
    file_type= Column(String(50))
    file_data= Column(LONGBLOB) # Changed from LargeBinary to LONGBLOB for larger files
    product_id= Column(Integer, ForeignKey("product.id")) # Added ForeignKey
    
