import psycopg2
from psycopg2 import sql
from msal import ConfidentialClientApplication
import requests
import os
from dotenv import load_dotenv

############################################################################################################################
######################################################### SHAREPOINT #######################################################
############################################################################################################################


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CERT_THUMBPRINT = os.getenv("CERT_THUMBPRINT")
TENANT_ID = os.getenv("TENANT_ID")
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")


# Get data from the AppRegistration
client_id = CLIENT_ID
cert_thumbprint = CERT_THUMBPRINT
tenant_id = TENANT_ID

# Define credentials
authority = f"https://login.microsoftonline.com/{tenant_id}"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDZ8BdfJ8fU0Hiv
pd+O+cY1lAjiBC+ksQCU2RRoZDG9GcNYSQi+UzLXhjHzmKg5CSWb1l1KIWc7z0oj
bhTYpFmszkz/qMOgPaSZQgTTn7dt7nejLHGKiPTFfi6t3vfNL17GoAAt62veXsH9
fqcZ14tyU3FHrGUap5Ah4amWx3W4f4GMM0qjrqpfU6jUqCiue0zPuf/gUnB5NbNy
y3LK3l7Kw7jBi5+VdvWyK/I4225RjGHzbyX7kVITwGiIiA3xLXa5eaecys4HhKZv
GLsYSK0IYc1iB1d7UkR/zE1I5spt/H7ZpuswUCXoeLuhZKmJczlYYVRULACqwh0U
WUIvO2CLAgMBAAECggEAE71bYJMJ1ozLYZ10kk6tVU0DQPWAGzqtAs5mus3Yc3hR
6T00PYjrofnVrGq3UfMyJNtVt9EuuIwd+veNi9HXDX/iGYX/shPjRL5mEYT16E8h
JvZvkky1Xu3+7GC1sTAJNZRob8BTFOEgUQWXvQ944fIM4KEMx01GEMuPwMhwMTWw
hATtwz9DFiEuvq4QIdAMd9jWwvcx7w3O2yAYIj5LKPO9e/D5b/x+8W3yPUCoB4Fs
Rm/paKLne0rpM3jSFQaPXGo6OwmHlNzGZDtEz3NjcnJb+16WDsmS9w3ZfkgZ4JRG
sUpOm/5cAwQJTxJVwJf2AMzVbXe3vLlOI427Kq67gQKBgQD1i4C7Y22xVcOTa73R
2btt3m2n/n+r2qsaYApCvzArW/ng2q881HEHjRQne85EwXuugi2+EPa6h5xhkvJ3
O/kvSJMKskqHLLVd+t3ZiAVtLf2SPvoJ8a5dUU2vT2cuWjBMfhYD7j3kNzgbHvOk
YGx9VOWaQNbGIR0SRR/kWxC9/QKBgQDjN6oz0JkF6lPXUDZLGx/b14nQ0VnNUfWk
ax+UsFHZarIa2SB3adLqGB3YDlmHDe66APIPOW0LjLpCXxI+ei3hMFCXKzOSIxMc
P7di04ggjNusZjgF41wQjl+K0hkiQhvtHWulbw3FbaCzAZgkxnN5ZKeeuF9axwMb
gW3dHvPbJwKBgD+MEA/vJpdri8cebizePbysgRKmMeKHIBseWel2U4AVOLExx4Jl
tK7wmxOw3ew7asf6Ft6Gw2P47sbt4eRr2Aydqrhs9g7Pykx9PWcr5cOg0GxF8i4a
pzatcP56/UgovTE+vHHd+ZSTmeii9QlIjytMinOGbk8uiLiOvTc7PjT9AoGBALTk
KRWNOXYzIsJk8oSCuK9d/jMHqHXEjUpzmjXW1aLAxcCIIcfPsQF7Z68NZYsWtXrR
q+Qg9MZgKB0U8UJaJNKFk3N2Cl2KnPk9ZLNB8rrvSSgMTQerBS2NG1U6hJX4iaER
bhTLv+vwpiI837JPZ7k6QBQldoyfqcKpHR0QOlW7AoGAZMXbeilHLWPA+30pYotG
joU1gBGczhA9PnBc8GPYpvXN/DhrVfvfUTobYRobtXAdE6jAzVnLCggnxWboGRC+
ZyQ9NzQG/q4P5qKgpnWantoKFqMhGAudglvAdKGFIfzJiapcVOCbYyexKqvpWxqd
mggm90Y3PzQTHF5aRNqqpU0=
-----END PRIVATE KEY-----
""" 

cert = {
    "private_key":private_key,
    "thumbprint":cert_thumbprint,
}

# Get token
msal_app = ConfidentialClientApplication(
    client_id=client_id,
    authority=authority,
    client_credential=cert,
)
scopes_sharepoint_online = ["https://ciindevelopers.sharepoint.com/.default"]
results=msal_app.acquire_token_for_cliente(scopes_sharepoint_online)
if "access_token" in results:
    access_token = results.get("access_token")
else:
    raise Exception("Error get token")


# Get data from the API Sharepoint - CashFlow Accounts List
headers = {
    "Authorization": f"Berar {access_token}",
    "Accept":"application/json;odata=verbose",
    "Content-Type":"aaplication/json",
}
sharepoint_base_url = "https://ciindevelopers.sharepoint.com/sites/FlujodeCaja"
sharepoint_url = f"{sharepoint_base_url}/_api/web/lists/GetByTitle('CashFlow - Account')/items"
response = requests.get(url=sharepoint_url,headers=headers)

#CashFlow Account List
response_data = response.json()
items_array = response_data['d']['results']

############################################################################################################################
######################################################### POSTGRES #########################################################
############################################################################################################################

# Set up DB connection
conn = psycopg2.connect(
    dbname="Sharepoint",
    user="postgres",
    password="admin",
    hsot="localhost",
    port="5432"
)

# Cursor
cur = conn.cursor()

# Define the query to insert data
query = sql.SQL("""
    INSERT INTO cashflow_account(id,name)
    VALUES (%s,%s)
    ON CONFLICT (id) DO NOTHING
                """)

# Prepare items_array to insert
for item in items_array:
    try:
        data = (item['ID'],item['Nombre'])
        cur.execute(query,data)
    except psycopg2.IntegrityError as e:
        print(f"Error integrity: {e}")
        conn.rollback()
    else:
        conn.commit()
        
# Close cursor and conn
cur.close()
conn.close()

print("ETL successful!")





