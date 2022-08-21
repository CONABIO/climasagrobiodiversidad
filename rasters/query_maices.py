import pandas as pd
import requests


def run_query(uri, query, statusCode):
    request = requests.post(uri, json={'query': query}, verify=False)
    if request.status_code == statusCode:
        return request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")


url="https://maices-siagro.conabio.gob.mx/api/graphql"
statusCode = 200

complete_dict = []
for i in range (0, 27):
    print(i)
    pagination = f'limit:1000, offset:{i*1000}'
    new_query = '{\n  registros(pagination:{' + pagination + '}){\n    id,\n    proyecto,\n    procedencia,\n    fecha_colecta_observacion,\n    taxon {\n      taxon_id\n      taxon\n      },\n    sitio{\n            latitud\n            longitud\n            estado\n            municipio\n            localidad\n    }           \n  }\n}\n'
    result = run_query(url, new_query, statusCode)
    complete_dict.append(result)

records = []
for i in range (len(complete_dict)):
    for j in range (len(complete_dict[i]['data']['registros'])):
        records.append(complete_dict[i]['data']['registros'][j])

#print(records)
df=pd.json_normalize(records)

df.to_csv('maices.csv')