
import re, math
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.cluster import AgglomerativeClustering



#------ NLP -------
def NLP(Documento):
  Doc = []
  for i in range(len(Documento)):
    d1 = Documento[i]
    #Eliminar carecteres especiales
    d1 = re.sub('[^A-Za-z0-9]+', ' ', d1)
    #Todas en minusculas
    d1 = d1.lower()
    #Tokenizar
    d1 = d1.split()
    #Stopwords
    stp = stopwords.words('english')
    for word in d1:
      if word in stp:
        d1.remove(word)
    #Stemming
    stemmer = PorterStemmer()
    for i in range(len(d1)):
      rem = stemmer.stem(d1[i])
      d1[i] = rem
    Doc.append(d1)
  return Doc

#------ Jacard ------
def Jacard(Documento):
  vec = []
  for i in range(len(Documento)):
    d = []
    for j in range(len(Documento)):
      t = list(set(Documento[i]+Documento[j]))
      tot = len(t)
      cont = 0
      for word in list(set(Documento[i])):
        if word in Documento[j]:
          cont += 1
      j = cont / tot
      d.append(round(j, 4))
    vec.append(d)
  return vec

#------ Coseno ------
def CosenoVectorial(d3):
  Diccionario = []
  for i in range(len(d3)):
    dic = d3[i]
    for j in range(len(dic)):
      Diccionario.append(dic[j])
  Diccionario = list(set(Diccionario))

  #Bag words
  V_Abstract = []
  for i in range(len(d3)):
    var = d3[i]
    cont = []
    for word in Diccionario:
      cont.append(var.count(word))
    V_Abstract.append(cont)

  #WTF
  V_W_Abstract = []
  for i in range(len(V_Abstract)):
    var = V_Abstract[i]
    cont = []
    for j in var:
      if j != 0:
        cont.append(1 + math.log(j,10))
      else:
        cont.append(0)
    V_W_Abstract.append(cont)

  #DF
  V_DF_Abstract = []
  for word in Diccionario:
    cont = 0
    for i in d3:
      if word in i:
        cont += 1
    V_DF_Abstract.append(cont)

  #IDF
  V_IDF_Abstract = []
  for i in V_DF_Abstract:
    V_IDF_Abstract.append(math.log(399 / i,10))

  #TF-IDF
  V_TF_IDF_Abstract = []
  for i in range(len(V_Abstract)):
    var = V_Abstract[i]
    cont = []
    for j in range(len(var)):
      cont.append(var[j] * V_IDF_Abstract[j])
    V_TF_IDF_Abstract.append(cont)

  #Modulo
  V_Mod_Abstract = []
  for i in range(len(V_W_Abstract)):
    var = V_W_Abstract[i]
    sum = 0
    for j in range(len(var)):
      sum = sum + var[j]**2
    V_Mod_Abstract.append(math.sqrt(sum))

  #Vector Unitario
  V_Uni_Abstract = []
  for i in range(len(V_W_Abstract)):
    var = V_W_Abstract[i]
    cont = []
    for j in range(len(var)):
      cont.append(var[j] / V_Mod_Abstract[i])
    V_Uni_Abstract.append(cont)

  #Coseno Vectorial
  V_Co_Abstract = []
  for i in range(len(V_Uni_Abstract)):
    var = V_Uni_Abstract[i]
    cont = []
    for j in range(len(V_Uni_Abstract)):
      sum = 0
      var2 = V_Uni_Abstract[j]
      for k in range(len(var2)):
        sum = sum + (var[k] * var2[k])
      cont.append(round(sum,4))
    V_Co_Abstract.append(cont)
  return V_Co_Abstract

#------ Multiplicar ------
def Mul_Vec(Vector,Multiplicar):
  for i in range(len(Vector)):
    t = Vector[i]
    for j in range(len(t)):
      t[j] = round(t[j] * Multiplicar, 4)
    Vector[i] = t
  return Vector

#------ Sumar ------
def Sum_Vec(Vec1,Vec2):
  V_Final = []
  for i in range(len(Vec1)):
    v_sum = Vec1[i]
    v1 = Vec1[i]
    v2 = Vec2[i]
    for j in range(len(Vec1)):
      v_sum[j] = round(v1[j] + v2[j], 4)
    V_Final.append(v_sum)
  return V_Final


def get_clusters():

  filename = 'data.csv'
  DataSet = pd.read_csv(filename,sep=';')

  categoria = DataSet.iloc[:, 1]
  producto = DataSet.iloc[:, 3]

  d1 = NLP(producto)
  d2 = NLP(categoria)

  V_Producto = Jacard(d1)
  V_Categoria = Jacard(d2)

  V_M_Productos = Mul_Vec(V_Producto,0.50)
  V_M_Categoria = Mul_Vec(V_Categoria,0.50)

  V_M_Final = Sum_Vec(V_M_Productos,V_M_Categoria)

  #DHC
  dhc = AgglomerativeClustering(n_clusters = 10, affinity = 'euclidean')
  grupos_dhc = dhc.fit_predict(V_M_Final)
  #dend = hierarchy.linkage(V_Producto, method='average', metric='euclidean')
  #plt.figure(figsize=(10, 8))
  #plt.title('Iris Dendograma DHC')
  #dendro = hierarchy.dendrogram(dend)
  #plt.show()

  return grupos_dhc