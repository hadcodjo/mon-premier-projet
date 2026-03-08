import streamlit as st
import pandas as pd

# ===============================
# CONFIGURATION PAGE
# ===============================

st.set_page_config(
    page_title="Financial App",
    layout="wide"
)

# ===============================
# TITRE
# ===============================

st.title("💎 Assistant de Gestion Financière")

st.write(
"Application de gestion des finances personnelles "
"avec visualisation et analyse."
)

# ===============================
# SIDEBAR
# ===============================

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "💰 Revenus",
        "📊 Dépenses",
        "📈 Analyse"
    ]
)

currency = st.sidebar.selectbox(
    "Devise",
    ["FCFA","€","$"]
)

# ===============================
# DASHBOARD
# ===============================

if page == "🏠 Dashboard":

    st.header("Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Revenus", "0")
    col2.metric("Dépenses", "0")
    col3.metric("Solde", "0")

# ===============================
# REVENUS
# ===============================

elif page == "💰 Revenus":

    st.header("Gestion des revenus")

    salaire = st.number_input("Salaire mensuel", min_value=0.0)

    revenu_sup = st.number_input("Revenus supplémentaires", min_value=0.0)

    if st.button("Ajouter revenu"):
        total = salaire + revenu_sup
        st.success(f"Revenu total ajouté : {total} {currency}")

# ===============================
# DEPENSES
# ===============================

elif page == "📊 Dépenses":

    st.header("Gestion des dépenses")

    categorie = st.selectbox(
        "Catégorie",
        ["Logement","Transport","Alimentation","Autres"]
    )

    montant = st.number_input("Montant", min_value=0.0)

    if st.button("Ajouter dépense"):
        st.success(f"Dépense enregistrée : {montant} {currency}")

# ===============================
# ANALYSE
# ===============================

elif page == "📈 Analyse":

    st.header("Analyse des dépenses")

    data = {
        "Categorie": ["Logement","Transport","Alimentation"],
        "Montant": [500,200,300]
    }

    df = pd.DataFrame(data)

    st.bar_chart(df.set_index("Categorie"))
