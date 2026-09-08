# 1. IMPORTAÇÃO DE BIBLIOTECAS
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

# 2. CARREGAMENTO E LIMPEZA DO DATAFRAME
df = pd.read_excel("carnivoros_limpo.xlsx")
print(df)

print(df.columns)
print(df["origem"].unique().tolist())
print(df["sp"].unique().tolist())

print(df[['sp', 'origem']].drop_duplicates().sort_values('sp')) # Conferindo se os nomes das espécies correspondem à origem delas

# 3. CALCULANDO O ÍNDICE DE IMPORTÂNCIA ALIMENTAR POR ESPÉCIE

# Selecionar itens alimentares (colunas que NÃO começam com % e NÃO são metadados)
metadados = ["coleta", "local", "individuo", "origem", "sp",
             "comp_total", "peso_total", "peso_estomago", "peso_conteudo"]

itens = [c for c in df.columns
         if c not in metadados and not c.startswith("%")]

def calcular_IAi_por_grupo(df, grupo_col):

    resultados = []

    grupos = df[grupo_col].unique()

    for grupo in grupos:
        sub = df[df[grupo_col] == grupo]

        # etapa 1: calcular Fi * Mi para todos os itens
        valores = {}
        for item in itens:
            Fi = (sub[item] > 0).mean()

            col_percent = f"%{item}"
            if col_percent in sub.columns:
                Mi = sub[col_percent].mean() / 100
            else:
                Mi = 0  # se não tiver %, assume zero

            valores[item] = Fi * Mi

        # etapa 2: somatório
        soma = sum(valores.values())

        # etapa 3: cálculo do IAi final
        for item, v in valores.items():
            IAi = v / soma if soma > 0 else 0
            resultados.append([grupo, item, IAi])

    return pd.DataFrame(resultados, columns=["grupo", "item", "IAi"])

# Calculando por espécie
iai_sp = calcular_IAi_por_grupo(df, "sp")

# Calculando por origem
iai_origem = calcular_IAi_por_grupo(df, "origem")

print("IAI por espécie")
print(iai_sp)
print("IAI por origem")
print(iai_origem)

# Salvando em excel
iai_sp.to_excel("iai_sp.xlsx", index=False) # salvando no excel
iai_origem.to_excel("iai_origem.xlsx", index=False)

# Calculando o índice de levins
# Dados
data = {
    "Item": [
        "Plant material",
        "Insects",
        "Unidentifiable digestive remains",
        "M. tuberculata",
        "Ostracota",
        "Zooplankton",
        "D. pagei",
        "Fish",
        "Incidental stones",
        "Shrimp",
        "Gastropoda",
        "Algae",
        "Soy",
        "Plastic particles"
    ],

    "Native": [
        0.374609,
        0.185502,
        0.003481,
        0.011488,
        0.000522,
        0.000261,
        0.000522,
        0.029242,
        0.000043,
        0.390325438,
        0.001740582,
        0.000870291,
        0.000696233,
        0.000696233
    ],

    "Invasive": [
        0.315508021,
        0.481283422,
        0.029168692,
        0.0,
        0.0,
        0.0,
        0.0,
        0.012639767,
        0.0,
        0.160427807,
        0.0,
        0.00097229,
        0.0,
        0.0
    ]
}

df = pd.DataFrame(data)

# Função para calcular o índice de Levins
def levins_index(proportions):
    return 1 / np.sum(np.square(proportions))

# Função para calcular o Levins padronizado
def levins_standardized(B, n):
    return (B - 1) / (n - 1)

# Número de categorias
n_items = len(df)

# Cálculo para nativos
B_native = levins_index(df["Native"])
Bsta_native = levins_standardized(B_native, n_items)

# Cálculo para invasores
B_invasive = levins_index(df["Invasive"])
Bsta_invasive = levins_standardized(B_invasive, n_items)

# Resultados
print("=== Levins Index ===")
print(f"Native: {B_native:.4f}")
print(f"Invasive: {B_invasive:.4f}")

print("\n=== Standardized Levins Index ===")
print(f"Native (Bsta): {Bsta_native:.4f}")
print(f"Invasive (Bsta): {Bsta_invasive:.4f}")

# Índice de Pianka
native = np.array([
    0.374609,
    0.185502,
    0.003481,
    0.011488,
    0.000522,
    0.000261,
    0.000522,
    0.029242,
    0.000043,
    0.390325438,
    0.001740582,
    0.000870291,
    0.000696233,
    0.000696233
])

invasive = np.array([
    0.315508021,
    0.481283422,
    0.029168692,
    0.0,
    0.0,
    0.0,
    0.0,
    0.012639767,
    0.0,
    0.160427807,
    0.0,
    0.00097229,
    0.0,
    0.0
])

# Função de Pianka
def pianka_index(p, q):
    numerator = np.sum(p * q)
    denominator = np.sqrt(np.sum(p**2) * np.sum(q**2))
    return numerator / denominator

# Cálculo
pianka = pianka_index(native, invasive)

print(f"Pianka Index: {pianka:.4f}")

print("Pianka")
print(pianka)

# NMDS
import numpy as np
import pandas as pd
from sklearn.manifold import MDS
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt

data = pd.DataFrame({
    "Item": [
        "Plant material",
        "Insects",
        "Unidentifiable digestive remains",
        "M. tuberculata",
        "Ostracoda",
        "Zooplankton",
        "D. pagei",
        "Fish",
        "Incidental stones",
        "Shrimp",
        "Gastropoda",
        "Algae",
        "Soy",
        "Plastic particles"
    ],
    "Native": [
        0.374609, 0.185502, 0.003481, 0.011488, 0.000522,
        0.000261, 0.000522, 0.029242, 0.000043, 0.390325438,
        0.001740582, 0.000870291, 0.000696233, 0.000696233
    ],
    "Invasive": [
        0.315508021, 0.481283422, 0.029168692, 0.0, 0.0,
        0.0, 0.0, 0.012639767, 0.0, 0.160427807,
        0.0, 0.00097229, 0.0, 0.0
    ]
})

# Matriz (transposta → linhas = espécies, colunas = itens)
diet_matrix = data[["Native", "Invasive"]].T.values

# ============================
# 2. Distância de Bray–Curtis
# ============================

dist_matrix = squareform(pdist(diet_matrix, metric="braycurtis"))

# ============================
# 3. NMDS (não-métrico)
# ============================

nmds = MDS(
    n_components=2,
    dissimilarity="precomputed",
    metric=False,
    max_iter=5000,
    eps=1e-12,
    random_state=42,
    n_init=50
)

nmds_coords = nmds.fit_transform(dist_matrix)

# ============================
# 4. Plot
# ============================

species_labels = ["Native", "Invasive"]

plt.figure(figsize=(7, 6))
plt.scatter(
    nmds_coords[:, 0],
    nmds_coords[:, 1],
    s=150
)

# Anotar nomes
for i, label in enumerate(species_labels):
    plt.text(
        nmds_coords[i, 0] + 0.005,
        nmds_coords[i, 1] + 0.005,
        label,
        fontsize=12
    )

plt.title("NMDS of Diet Composition (Bray–Curtis)", fontsize=14)
plt.xlabel("NMDS1")
plt.ylabel("NMDS2")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
