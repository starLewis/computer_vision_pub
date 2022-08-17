from odata import ODataService
from requests_ntlm import HttpNtlmAuth
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import requests

userAccount = 'danj@REGREBENdemo01.onmicrosoft.com'
domain ='https://regrebendemo11.api.crm4.dynamics.com'
password = 'cloudServus9!'

credential = {userAccount, password, domain}

my_headers = {
    'UserAccount':userAccount,
    'Password':password,
    'Domain':domain
}

# url = 'http://services.odata.org/V4/Northwind/Northwind.svc/'
url = "https://regrebendemo11.api.crm4.dynamics.com/api/data/v9.1/msdyn_iotalerts"
# # basic_url = "https://regrebendemo11.api.crm4.dynamics.com"
# my_auth = ('danj@REGREBENdemo01.onmicrosoft.com', 'cloudServus9!')
result = requests.get(url, headers = my_headers)
print result.status_code

# my_headers = {
#     'content-type':'application/json',
#     'odata-version':'4.0',
#     'req_id':'437b02da-b152-4428-a9a9-107423769137',
# }

# result = requests.get(url, headers = my_headers)
# print result.content


# my_session = requests.Session()
# my_session.auth = HttpNtlmAuth('danj@REGREBENdemo01.onmicrosoft.com', 'cloudServus9!')
# result = my_session.get(basic_url)
# print result
# Service = ODataService(url, session=my_session)
# IOT = Service.entities['msdyn_iotalerts']
# query = Service.query(msdyn_iotalerts)

# print Service

# print query.all()

# data = {'Description':'cl_test_01', 
#         'Account':'GETEC green energy AG',
#         'PictureURL':'http://filewind.clobotics.cn/api/file/2d1ddac73b71c3ba4df87da2c878e19d',
#         'Details':'clobotics test 01'
#         }
# result = my_session.post(url, data)
# print result

# result = requests.get(url, auth=my_auth)
# result = requests.post(url, auth=my_auth, json=data)

# print result.text
# Service = ODataService(url, reflect_entities=True, auth = my_auth)
# qurey = Service.query(IoT Alerts)

# print query.all()
# ID = Service.entities['ID']

# query = Service.query(ID)
# query = query.limit(2)
# query = query.order_by(ID.CompanyName.asc())

# for supplier in query:
#     print('Company:', supplier.CompanyName)

#     for product in supplier.Products:
#         print('- Product:', product.ProductName)