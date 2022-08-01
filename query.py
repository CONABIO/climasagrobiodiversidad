import pandas as pd
import requests

def run_query(uri, query, statusCode):
    request = requests.post(uri, json={'query': query}, verify=False)
    if request.status_code == statusCode:
        return request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")


url="https://siagro.conabio.gob.mx/maices_api"
statusCode = 200

complete_dict = []
for i in range (0, 27):
    pagination = f'limit:1000, offset:{i*1000}'
    new_query = '{\n  ejemplars(pagination:{' + pagination + '}){\n    id,\n    especievalida,\n    longitud,\n    latitud,\n    paismapa,\n    estadomapa,\n    municipiomapa,\n    localidad,\n    clavemunicipiomapa,\n    altitudmapa,\n    procedenciaejemplar,\n    coleccion,\n    institucion,\n    aniocolecta,\n    mescolecta,\n    diacolecta,\n    proyecto,\n    fuente,\n    formadecitar,\n    licenciauso,\n    version           \n  }\n}\n'
    result = run_query(url, new_query, statusCode)
    complete_dict.append(result)

records = []
for i in range (len(complete_dict)):
    for j in range (len(complete_dict[i]['data']['ejemplars'])):
        records.append(complete_dict[i]['data']['ejemplars'][j])

df = pd.DataFrame.from_dict(records)

df.to_csv('maices.csv')