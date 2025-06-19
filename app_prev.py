import streamlit as st
import pandas as pd
from datetime import datetime
import io


st.set_page_config(layout="wide")

aujourd_hui_str = datetime.today().strftime("%d/%m/%Y") #définir la date du jour
st.markdown(f"**Affichage des paiements à venir à partir du : {aujourd_hui_str}**")

# === Demande chargement du fichier de commande frn === #
uploaded_file = st.sidebar.file_uploader("📁 Importez un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Lire le fichier selon son extension
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if df.shape[1] < 35:
        st.warning("Le fichier semble vide ou mal formé.")
    else:
        st.success("Fichier chargé avec succès ✅")
        st.write("Aperçu des données :")


    # === Chargement du Google Sheet Condition fournisseur === #
    sheet_id = "1E6jf5bBgCz_k_pY13iGoSLtd2vrQDnuV" 
    sheet_name = "ALL_GAMME"  

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    df_cond = pd.read_csv(url)


    # === Traitement des fichiers ensemble === #

    df.columns = df.columns.str.strip() # Supprimer les espaces des colonnes df
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


    # Renommer les colonnes
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
    
    df = df.dropna(subset=["CONDITION DE PAIEMENTS"])


    # == Construire un nouveau dataframe de prévisions == #

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
            st.warning(f"❗ Condition non gérée : '{condition}' à l'index {index}")

    


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
    df_paiements['date_paiement_formatee'] = df_paiements['date_paiement'].dt.strftime('%d/%m/%Y')

    # Formater les valeurs de mes colonnes
    df_paiements["montant"] = df_paiements["montant"].apply(lambda x: f"{int(round(x)):,}".replace(",", " "))
    df_paiements = df_paiements[df_paiements["code_fournisseur"].notna()]
    df_paiements["code_fournisseur"] = df_paiements["code_fournisseur"].astype(int)
    df_paiements["numero_commande"] = df_paiements["numero_commande"].astype(int)




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

# === 1. Fonctions ===


def filtrer_paiements_a_venir(df_paiements, colonne_date="date_paiement"):
    df_paiements[colonne_date] = pd.to_datetime(df_paiements[colonne_date]) # S'assurer que la colonne est bien en datetime
    aujourd_hui = pd.to_datetime(datetime.today().date()) # Filtrer à partir d'aujourd'hui inclus
    df_filtre = df_paiements[df_paiements[colonne_date] >= aujourd_hui]
    return df_filtre


def appliquer_filtres(df_paiements, gamme, fournisseur, devise, condition,numero_commande):
    if gamme != "Toutes":
        df_paiements = df_paiements[df_paiements["gamme"] == gamme]
    if fournisseur != "Toutes":
        df_paiements = df_paiements[df_paiements["fournisseur"] == fournisseur]
    if devise != "Toutes":
        df_paiements = df_paiements[df_paiements["devise"] == devise]
    if condition != "Toutes":
        df_paiements = df_paiements[df_paiements["condition"] == condition]
    if numero_commande != "Toutes":
        df_paiements = df_paiements[df_paiements["numero_commande"] == numero_commande]
    return df_paiements


def get_fournisseurs_par_gamme(df_paiements, gamme): #venir rendre dépendant le filtre frn par la gamme
    if gamme == "Toutes":
        return df_paiements["fournisseur"].unique().tolist()
    else:
        return df_paiements[df_paiements["gamme"] == gamme]["fournisseur"].unique().tolist()
    
def get_numerocmde_par_frn(df_paiements, fournisseur):
    if fournisseur == "Toutes":
        return df_paiements["numero_commande"].unique().tolist()
    else:
        return df_paiements[df_paiements["fournisseur"] == fournisseur]["numero_commande"].unique().tolist()



def afficher_tableau(df): 
    df_sorted = df_paiements.sort_values("date_paiement", ascending=True) # Trier par date du plus ancien au plus récent (colonne "date_paiement" reste colonne normale)
    styled_df = df_sorted.style.set_properties(**{'text-align': 'center'})\
                                .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]) # Appliquer le style centré (colonnes et en-têtes)
    st.dataframe(styled_df, use_container_width=True, height=600) # Afficher dans Streamlit avec scrolling et largeur dynamique


def selectionner_colonnes(df_paiements):
    colonnes = ["date_paiement_formatee","code_fournisseur", "semaine", "mois" ,"fournisseur", "montant", "devise", "gamme", "numero_commande", "condition", "date_paiement"]
    return df_paiements[colonnes]


# === 2. Chargement des données ===

if uploaded_file is not None:
    df_paiements = filtrer_paiements_a_venir(df_paiements)


    # === 3. UI : Titre ===

    st.title("💎 Prévisions des paiements fournisseurs")
    st.text("Ci dessous les prévisions paiements. Seules les commandes après date du jour sont affichées. Donc ne prends pas en compte toutes les commandes en cours mais seulement celles à prévoir dans les prévisions.")
    st.markdown("**Paiement à venir :**")





    # === 4. UI : Filtres ===

    st.sidebar.title("Filtres")

    gamme = st.sidebar.selectbox("Choisir une gamme", options=["Toutes"] + df_paiements["gamme"].unique().tolist())
    fournisseurs_disponibles = get_fournisseurs_par_gamme(df_paiements, gamme)
    fournisseur = st.sidebar.selectbox("Choisir un fournisseur", options=["Toutes"] + fournisseurs_disponibles)
    devise = st.sidebar.selectbox("Choisir une devise", options=["Toutes"] + df_paiements["devise"].unique().tolist())
    condition = st.sidebar.selectbox("Choisir une condition", options=["Toutes"] + df_paiements["condition"].unique().tolist())
    numcmde_disponibles = get_numerocmde_par_frn(df_paiements, fournisseur)
    numero_commande = st.sidebar.selectbox("Choisir une commande", options=["Toutes"] + numcmde_disponibles)





    # === 5. Application des filtres ===

    df_paiements = appliquer_filtres(df_paiements, gamme, fournisseur, devise, condition, numero_commande)


    # === 4.  : KPI ===

    st.write("## Prévisions totales")
    col1, col2 = st.columns(2)

    with col1:
        total_usd = df_paiements["montant_usd"].sum()
        total_usd_formate = f"{total_usd:,.0f}".replace(",", " ") + " $"
        st.metric("Montant paiement en $ à prévoir", total_usd_formate)
    with col2:
        total_eur = df_paiements["montant_eur"].sum()
        total_eur_formate = f"{total_eur:,.0f}".replace(",", " ") + " €"
        st.metric("Montant paiement en € à prévoir", total_eur_formate)

    df_paiements = selectionner_colonnes(df_paiements)


    # === 6. Affichage final ===

    afficher_tableau(df_paiements)

else:
    st.info("Veuillez importer un fichier pour afficher les prévisions de paiement.")

