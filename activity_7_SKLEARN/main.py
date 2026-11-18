from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

#carregar dados
wine = load_wine(as_frame = True)

wine.data.head()

X = wine.data
y = wine.target

print("Formato de X:", X.shape)
print("Formato de y:", y.shape)

print("\nClasses existentes:")
print(y.unique())

#dividir os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify = y)

print("Quantidade de dados de treino:", len(X_train))
print("Quantidade de dados de teste:", len(X_test))

#construção dos modelos
modelo_logistico = Pipeline([
    ('scaler', StandardScaler()),
    ('modelo', LogisticRegression(max_iter=1000, random_state=42))
])

modelo_knn = Pipeline([
    ('scaler', StandardScaler()),
    ('modelo', KNeighborsClassifier(n_neighbors=5))
])

#validação cruzada
scores_logistico = cross_val_score(
    modelo_logistico,
    X_train,
    y_train,
    cv=5
)
print("Resultados da Regressão Logística:")
print(scores_logistico)

print("\nMédia dos resultados:")
print(scores_logistico.mean())

print("\nDesvio padrão:")
print(scores_logistico.std())

scores_knn = cross_val_score(
    modelo_knn,
    X_train,
    y_train,
    cv=5
)
print("Resultados do KNN:")
print(scores_knn)

print("\nMédia dos resultados:")
print(scores_knn.mean())

print("\nDesvio padrão:")
print(scores_knn.std())

#comparação entre os modelos
import pandas as pd

resultados = pd.DataFrame({
    'Modelo': ['Regressão Logística', 'KNN'],
    'Acurácia Média': [
        scores_logistico.mean(),
        scores_knn.mean()
    ],
    'Desvio Padrão': [
        scores_logistico.std(),
        scores_knn.std()
    ]
})
print(resultados)

#treinamento dos modelos
modelo_logistico.fit(X_train, y_train)
modelo_knn.fit(X_train, y_train)

#avaliação dos modelos
y_pred_logistico = modelo_logistico.predict(X_test)
y_pred_knn = modelo_knn.predict(X_test)

acuracia_logistico = accuracy_score(y_test, y_pred_logistico)
acuracia_knn = accuracy_score(y_test, y_pred_knn)

print("Acurácia da Regressão Logística:", acuracia_logistico)
print("Acurácia do KNN:", acuracia_knn)

print('Regressão Logística')
print(classification_report(y_test, y_pred_logistico))

print("KNN")
print(classification_report(y_test, y_pred_knn))

#Matriz de confusão
if acuracia_logistico >= acuracia_knn:
    melhor_modelo = modelo_logistico
    melhor_predicao = y_pred_logistico
    nome_modelo = "Regressão Logística"
else:
    melhor_modelo = modelo_knn
    melhor_predicao = y_pred_knn
    nome_modelo = "KNN"

print("Melhor modelo:", nome_modelo)

matriz = confusion_matrix(y_test, melhor_predicao)

disp = ConfusionMatrixDisplay(
    confusion_matrix=matriz,
    display_labels=wine.target_names
)

disp.plot(cmap='Blues')

plt.title(f'Matriz de Confusão - {nome_modelo}')
plt.show()