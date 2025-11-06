import pandas as pd
import requests
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

'''
========================
    Config
========================
'''

debug_mode = True

headers = os.getenv("headers")
headers = {"X-Api-Authorization" : headers}
url_1 = os.getenv("url_1")
url_2 = os.getenv("url_2")
url_3 = os.getenv("url_3")


local = "data.xlsx"
excel_categorias = "categorias.csv"
excel_segmentos = "segmentos.csv"
excel_objetos = "objetos.csv"

for file in [excel_categorias, excel_segmentos, excel_objetos]:
    if not os.path.exists(file):
        pd.DataFrame(columns=['ID', 'PREFIXO', 'DESCRICAO']).to_csv(file, sep=';', index=False)

 
tipos_categoria : list = []
tipos_segmentos : list = []
tipos_objetos : list = []

df_cat = pd.read_csv(excel_categorias, sep=';')
df_seg = pd.read_csv(excel_segmentos, sep=';')
df_objt = pd.read_csv(excel_objetos, sep=';')

'''
========================
    Classes
========================
'''

class item:
  def __init__(self, 
               id : str,
               prefixo : str,
               descricao : str, 
               tipo : str):
    self.id = id
    self.prefixo = prefixo
    self.descricao = descricao
    self.tipo = tipo
    
  def __str__(self):
    return f"ID: {self.id} | Prefixo: {self.prefixo} | Descrição: {self.descricao} | Tipo: {self.tipo}"
 
 
'''
========================
    Limpeza de Tipos
========================
'''
 
# UNICOS DO EXCEL VÃO FILTRAR TIPO DE DADOS DA API

df = pd.read_excel(local) 
tipos_categoria = df['CATEGORIA'].unique().tolist()
tipos_segmentos = df['SEGMENTO'].unique().tolist()
tipos_objetos = df['Objeto'].unique().tolist()
 
if debug_mode:
  print('categoria', tipos_categoria)
  print('segmentos', tipos_segmentos)
  print('objetos', tipos_objetos)
 

'''
========================
    Functions
========================
'''
 
 
def popula_dados(campo_id : str,
                campo_prefixo : str,
                campo_descricao : str,
                tipo_item : str,
                lista_infos : list):
  global df_cat, df_seg, df_objt
  
  for lista in lista_infos:
    
    id = lista[campo_id]
    prefixo = lista[campo_prefixo]
    descricao = lista[campo_descricao]
    
    item_novo = item(id=id,
                     prefixo=prefixo,
                     descricao=descricao,
                     tipo = tipo_item)

    
    if debug_mode:
      print(f"${item_novo}")
    
    
    new_row = pd.DataFrame({'ID' : [item_novo.id], 
                            'PREFIXO' : [item_novo.prefixo], 
                            'DESCRICAO' : [item_novo.descricao]})
    
    if item_novo.tipo == "categoria":
     df_cat = pd.concat([df_cat, new_row], ignore_index=True)
    elif item_novo.tipo == "segmento":
      df_seg = pd.concat([df_seg, new_row], ignore_index=True)
    elif item_novo.tipo == "quartenario":
      df_objt = pd.concat([df_objt, new_row], ignore_index=True)
      

    
    

def get_data(url : str, ) -> list:
  r = requests.get(url=url, headers=headers) 
  if r.status_code == 200:
    data = r.json()
    lista_infos : list = data["data"]["rows"]
    return lista_infos
  else:
    print(f"Requisição morreu : ${r.status_code}" )
    

def valida_tipos_unicos(df : pd.DataFrame, lista_tipos : list, campo_validado : str):
  for campo in df[campo_validado]:
    for tipo in lista_tipos:
      if campo not in lista_tipos:
        df.drop(df[df[campo_validado] == campo].index, inplace=True)
  
    
 
 
'''
========================
    Main
========================
'''
 
lista_1 = get_data(url_1)
lista_2 = get_data(url_2)
lista_3 = get_data(url_3)


popula_dados('cat_id', 'cat_prefixo', 'cat_descricao', "categoria", lista_1)
popula_dados('seg_id', 'seg_prefixo', 'seg_descricao', "segmento", lista_2)
popula_dados('qua_id', 'qua_prefixo', 'qua_descricao', "quartenario", lista_3)


valida_tipos_unicos(df_cat, tipos_categoria, 'DESCRICAO')
valida_tipos_unicos(df_seg, tipos_segmentos, 'DESCRICAO')
valida_tipos_unicos(df_objt, tipos_objetos, 'DESCRICAO')

'''
========================
    Salvando arquivos
========================
'''

with pd.ExcelWriter("dados_atualizados.xlsx") as writer:
    df_cat.to_excel(writer, sheet_name="Categorias", index=False)
    df_seg.to_excel(writer, sheet_name="Segmentos", index=False)
    df_objt.to_excel(writer, sheet_name="Objetos", index=False)

print("✅ Dados salvos em 'dados_atualizados.xlsx'")
