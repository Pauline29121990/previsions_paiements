import pandas as pd
import numpy as np
import streamlit as st
import os

# Chemins vers les dossiers
chemin_input = "/Users/paulinem/Documents/Documents_popo/Formation_Data/VS_Code/Projet_pro/Prévisions_paiements/Commandes_fournisseurs/"
chemin_output = "/Users/paulinem/Documents/Documents_popo/Formation_Data/VS_Code/Projet_pro/Prévisions_paiements/Prévisions_export"

'''# Cherche un fichier qui commence par "commande-fournisseurs" dans le dossier input
for nom_fichier in os.listdir(chemin_input):
    if nom_fichier.startswith("commande-fournisseurs"):
        chemin_fichier = os.path.join(chemin_input, nom_fichier)
        break
else:
    raise FileNotFoundError("Aucun fichier 'commande-fournisseurs' trouvé dans le dossier.")

# Chargement du fichier (en fonction de l'extension)
if chemin_fichier.endswith(".xlsx"):
    df = pd.read_excel(chemin_fichier)
elif chemin_fichier.endswith(".csv"):
    df = pd.read_csv(chemin_fichier)
else:
    raise ValueError("Le fichier trouvé n'est ni un .csv ni un .xlsx")

print("✅ Fichier chargé avec succès :")
print(df.head())'''


'''#ID du Google Sheet Condition fournisseur
sheet_id2 = "1E6jf5bBgCz_k_pY13iGoSLtd2vrQDnuV" 
sheet_name2 = "ALL_GAMME"  

url2 = f"https://docs.google.com/spreadsheets/d/{sheet_id2}/gviz/tq?tqx=out:csv&sheet={sheet_name2}"


# Lire les données dans pandas
df_cond = pd.read_csv(url2)'''


'''df.columns = df.columns.str.strip() # Supprimer les espaces des colonnes df
df_cond.columns = df_cond.columns.str.strip() # Supprime les espaces des colonnes df_cond

# Supprimer les colonnes inutiles du df (export auto)
df.drop(columns=
                ["en_type_confie",
                "fo_ref_cli",
                "td_color_w",
                "num_fac",
                "facture",
                "en_valeur_devise",
                "num_br",
                "en_num_livraison",
                "en_mt_suppl",
                "ed_etat",
                "en_num_doc_ref",
                "en_frais_taxe",
                "en_frais_non_taxe",
                "en_acompte",
                "en_escompte",
                "en_transf_bij_psion",
                "fo_edi_type",
                "en_edi",
                "ed_code",
                "active"],
        
        axis=1 ,inplace=True)



# Afficher les valeurs nulles
nul_df = (df.isnull().sum())
nul_df_cond = (df_cond.isnull().sum())'''

'''# Renommer les colonnes
df.rename(columns={
    'td_code': 'type_commande',
    'en_date_doc': 'date_document',
    'fo_code': 'code_fournisseur',
    'en_etat_facture': 'etat_facture',
    'en_num_doc': 'numero_document',
    'en_code': 'Inconnu',
    'en_num_ext': 'raison_commande',
    'de_code': 'devise',
    'fo_raison_soc': 'nom_fournisseur',
    'num_com': 'numero_commande',
    'etat_lib': 'etat_document',
    'en_date2': 'date_livraison',
    'en_qte_doc': 'quantites',
    'en_mt_doc': 'montant',
    'en_date_paye': 'date_depart',
    }, inplace=True)


df_cond.rename(columns={
    'FO_CODE': 'code_fournisseur',
    }, inplace=True)


# Conversion des colonnes de dates colonne en datetime
df["date_document"] = pd.to_datetime(df["date_document"], format="%d/%m/%Y %H:%M:%S", dayfirst=True, errors="coerce")
df["date_livraison"] = pd.to_datetime(df["date_livraison"], format="%d/%m/%Y %H:%M:%S", dayfirst=True, errors="coerce")
df["date_depart"] = pd.to_datetime(df["date_depart"], format="%d/%m/%Y %H:%M:%S", dayfirst=True, errors="coerce")

# Merger mes deux df avec la colonne Condition de Paiements
df = df.merge(df_cond[["CONDITION DE PAIEMENTS", "code_fournisseur", "GAMME"]], on="code_fournisseur", how="left")


df["montant"] = df["montant"].str.replace(',', '.', regex=False)
df["montant"] = pd.to_numeric(df["montant"], errors="coerce")
print(df["montant"].dtype)

df["CONDITION DE PAIEMENTS"].isnull().sum()
df = df.dropna(subset=["CONDITION DE PAIEMENTS"])'''



paiements = []

for index, row in df.iterrows():
    fournisseur = row["nom_fournisseur"]
    condition = row["CONDITION DE PAIEMENTS"]
    montant_total = row["montant"]
    date_commande = row["date_document"]
    date_livraison = row["date_livraison"]
    numero_commande = row["numero_commande"]
    devise = row['devise']
    gamme = row['GAMME']
    code_four = row['code_fournisseur']

    
    condition = str(condition).strip().upper()

    if condition == "60J":
        date_paiement = date_livraison + pd.Timedelta(days=60)
        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_paiement,
            "montant": montant_total,
            "condition": condition,
            "devise": devise,
            "fournisseur": fournisseur,
            "gamme": gamme,
            "code_fournisseur": code_four
        })

    elif condition == "J30":
        date_paiement = date_livraison + pd.Timedelta(days=30)
        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_paiement,
            "montant": montant_total,
            "condition": condition,
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

    elif condition == "AVANT EXPEDITION":
        date_paiement = date_livraison
        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_paiement,
            "montant": montant_total,
            "condition": condition,
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

    elif condition in ["30% DEPOSIT 70% J60", "DEPOSIT 30% + J+60"]:
        montant_deposit = montant_total * 0.30
        montant_restant = montant_total - montant_deposit

        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_commande,
            "montant": montant_deposit,
            "condition": condition + " - deposit",
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

        date_solde = date_commande + pd.Timedelta(days=60)
        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_solde,
            "montant": montant_restant,
            "condition": condition + " - solde",
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

    elif condition in ["30 %COMMANDE 70 %LIVRAISON", "30% COMMANDE 70% LIVRAISON"]:
        # Hypothèse : même logique qu’un deposit 30%
        montant_deposit = montant_total * 0.30
        montant_restant = montant_total - montant_deposit

        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_commande,
            "montant": montant_deposit,
            "condition": condition + " - deposit estimé",
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

        date_solde = date_livraison
        paiements.append({
            "index_commande": index,
            "numero_commande": numero_commande,
            "date_paiement": date_solde,
            "montant": montant_restant,
            "condition": condition + " - solde",
             "devise": devise,
             "fournisseur": fournisseur,
             "gamme": gamme,
            "code_fournisseur": code_four
        })

    else:
        print(f"❗ Condition non gérée : '{condition}' à l'index {index}")
 


# Création du nouveau DataFrame avec les lignes de paiement
df_paiements = pd.DataFrame(paiements)



# On crée les deux colonnes montant_eur et montant_usd en fonction de la devise
df_paiements["montant_eur"] = df_paiements.apply(
    lambda row: row["montant"] if row["devise"] == "E" else 0,
    axis=1
)

df_paiements["montant_usd"] = df_paiements.apply(
    lambda row: row["montant"] if row["devise"] == "$" else 0,
    axis=1)

#Convertir la colonne date de paiement en format date 
df_paiements["date_paiement"] = pd.to_datetime(df_paiements["date_paiement"], errors="coerce")


#Convertir les dates en semaines et en mois

df_paiements["semaine"] = df_paiements["date_paiement"].dt.to_period('W').astype(str)
df_paiements["mois"] = df_paiements["date_paiement"].dt.to_period('M').astype(str)

paiements_par_semaine_euros = df_paiements.groupby("semaine")["montant_eur"].sum().reset_index()
paiements_par_mois_euros = df_paiements.groupby("mois")["montant_eur"].sum().reset_index()

paiements_par_semaine_usd = df_paiements.groupby("semaine")["montant_usd"].sum().reset_index()
paiements_par_mois_usd = df_paiements.groupby("mois")["montant_usd"].sum().reset_index()


# Supprime les lignes entièrement vides ou avec des dates manquantes
df_paiements = df_paiements.dropna(how="all")
df_paiements = df_paiements[df_paiements["date_paiement"].notna()]
df_paiements = df_paiements[df_paiements["montant"].notna()]

# Debug final
print("🧹 Taille avant nettoyage :", df_paiements.shape)
df_paiements = df_paiements.dropna(subset=["date_paiement", "montant"])
print("🧽 Taille après nettoyage :", df_paiements.shape)

# Enregistrement du fichier de sortie
chemin_sortie = os.path.join(chemin_output, "previsions_paiements.xlsx")
df_paiements.to_excel(chemin_sortie, index=False)


print("👉 Lignes complètement vides :", df_paiements[df_paiements.isnull().all(axis=1)])
print(f"✅ Fichier de sortie enregistré ici : {chemin_sortie}")