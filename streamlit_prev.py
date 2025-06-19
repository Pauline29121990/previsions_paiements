import streamlit as st
import pandas as pd
from datetime import datetime


st.set_page_config(layout="wide")

aujourd_hui_str = datetime.today().strftime("%d/%m/%Y") #définir la date du jour
st.markdown(f"**Affichage des paiements à venir à partir du : {aujourd_hui_str}**")


# === 1. Fonctions ===


def filtrer_paiements_a_venir(df, colonne_date="date_paiement"):
    df[colonne_date] = pd.to_datetime(df[colonne_date]) # S'assurer que la colonne est bien en datetime
    aujourd_hui = pd.to_datetime(datetime.today().date()) # Filtrer à partir d'aujourd'hui inclus
    df_filtre = df[df[colonne_date] >= aujourd_hui]
    return df_filtre

def charger_donnees(chemin_fichier):
    return pd.read_excel(chemin_fichier)

def appliquer_filtres(df, gamme, fournisseur, devise, condition,numero_commande):
    if gamme != "Toutes":
        df = df[df["gamme"] == gamme]
    if fournisseur != "Toutes":
        df = df[df["fournisseur"] == fournisseur]
    if devise != "Toutes":
        df = df[df["devise"] == devise]
    if condition != "Toutes":
        df = df[df["condition"] == condition]
    if numero_commande != "Toutes":
        df = df[df["numero_commande"] == numero_commande]
    return df


def get_fournisseurs_par_gamme(df, gamme): #venir rendre dépendant le filtre frn par la gamme
    if gamme == "Toutes":
        return df["fournisseur"].unique().tolist()
    else:
        return df[df["gamme"] == gamme]["fournisseur"].unique().tolist()
    
def get_numerocmde_par_frn(df, fournisseur):
    if fournisseur == "Toutes":
        return df["numero_commande"].unique().tolist()
    else:
        return df[df["fournisseur"] == fournisseur]["numero_commande"].unique().tolist()



def afficher_tableau(df): 
    df_sorted = df.sort_values("date_paiement", ascending=True) # Trier par date du plus ancien au plus récent (colonne "date_paiement" reste colonne normale)
    styled_df = df_sorted.style.set_properties(**{'text-align': 'center'})\
                                .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]) # Appliquer le style centré (colonnes et en-têtes)
    st.dataframe(styled_df, use_container_width=True, height=600) # Afficher dans Streamlit avec scrolling et largeur dynamique


def selectionner_colonnes(df):
    colonnes = ["date_paiement","code_fournisseur", "semaine", "mois" ,"fournisseur", "montant", "devise", "gamme", "numero_commande", "condition"]
    return df[colonnes]


# === 2. Chargement des données ===

chemin_fichier = "/Users/paulinem/Documents/Documents_popo/Formation_Data/VS_Code/Projet_pro/Prévisions_paiements/Prévisions_export/previsions_paiements.xlsx"
df = charger_donnees(chemin_fichier)
df = filtrer_paiements_a_venir(df)


# === 3. UI : Titre ===

st.title("💎 Prévisions des paiements fournisseurs")
st.text("Ci dessous les prévisions paiements. Seules les commandes après date du jour sont affichées. Donc ne prends pas en compte toutes les commandes en cours mais seulement celles à prévoir dans les prévisions.")
st.markdown("**Paiement à venir :**")



# === 4. UI : Filtres ===

st.sidebar.title("Filtres")

gamme = st.sidebar.selectbox("Choisir une gamme", options=["Toutes"] + df["gamme"].unique().tolist())
fournisseurs_disponibles = get_fournisseurs_par_gamme(df, gamme)
fournisseur = st.sidebar.selectbox("Choisir un fournisseur", options=["Toutes"] + fournisseurs_disponibles)
devise = st.sidebar.selectbox("Choisir une devise", options=["Toutes"] + df["devise"].unique().tolist())
condition = st.sidebar.selectbox("Choisir une condition", options=["Toutes"] + df["condition"].unique().tolist())
numcmde_disponibles = get_numerocmde_par_frn(df, fournisseur)
numero_commande = st.sidebar.selectbox("Choisir une commande", options=["Toutes"] + numcmde_disponibles)





# === 5. Application des filtres ===

df = appliquer_filtres(df, gamme, fournisseur, devise, condition, numero_commande)


# === 4.  : KPI ===

st.write("## Prévisions totales")
col1, col2 = st.columns(2)

with col1:
    total_usd = df["montant_usd"].sum()
    total_usd_formate = f"{total_usd:,.0f}".replace(",", " ") + " $"
    st.metric("Montant paiement en $ à prévoir", total_usd_formate)
with col2:
    total_eur = df["montant_eur"].sum()
    total_eur_formate = f"{total_eur:,.0f}".replace(",", " ") + " €"
    st.metric("Montant paiement en € à prévoir", total_eur_formate)

df = selectionner_colonnes(df)


# === 6. Affichage final ===

afficher_tableau(df)
