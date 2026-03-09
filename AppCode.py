pip install -r requirements.txt
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from datetime import datetime
import os

# ===============================
# CONFIGURATION DE LA PAGE STREAMLIT
# ===============================
# Configure les paramètres de base de la page Streamlit.
st.set_page_config(
    layout="wide",                     # Utilise une mise en page large pour mieux utiliser l'espace
    initial_sidebar_state="expanded")  # La barre latérale est ouverte par défaut

# ===============================
# DESIGN ET STYLE CSS PERSONNALISÉ
# ===============================
# Injecte du CSS personnalisé pour styliser l'application, en particulier le fond
# et les titres pour une meilleure esthétique.
st.markdown("""
<style>
.main {
    background: linear-gradient(to right, #f8f9fa, #e9f2ff); /* Dégradé de fond */
}
.big-title {
    font-size: 48px;
    font-weight: 800;
    color: #1f4e79; /* Couleur foncée pour le titre principal */
}
.subtitle {
    font-size: 18px;
    color: #6c757d; /* Couleur plus douce pour le sous-titre */
}
.metric-card {
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.metric-card-revenue {
    background: linear-gradient(135deg, #06a77d, #28a745); /* Vert pour les revenus */
}
.metric-card-expense {
    background: linear-gradient(135deg, #de1f12, #dc3545); /* Bleu pour les dépenses */
}
.metric-card-balance {
    background: linear-gradient(135deg, #0657a7, #007bff); /* Rouge pour le solde */
}
.section-title-blue {
    font-size: 36px;
    font-weight: 700;
    color: #007bff; /* Bleu pour les titres de section */
    margin-bottom: 20px; /* Espace sous le titre */
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if "revenues" not in st.session_state:
    st.session_state.revenues = []

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
        "📈 Analyse",
        "🤖 AI Conseiller"
    ])

currency = st.sidebar.selectbox(
    "💱 Devise",
    ["FCFA", " € ", " $ "])

st.sidebar.markdown("---")
st.sidebar.markdown("#### Réalisé par")
st.sidebar.markdown("""
**👤 Had CODJO**
🔗 [LinkedIn](https://urlr.me/ap9PGY)
""")
st.sidebar.markdown("""
**👤 Bamory CISSE**
🔗 [LinkedIn](linkedin.com/in/bamory-cisse-116b02105)
""")

# ===============================
# DASHBOARD
# ===============================
if page == "🏠 Dashboard":
    st.markdown('<div class="big-title">💎 Assistant de Gestion Financière</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle"> Application de gestion des finances personnelles avec visualisation et analyse.</div>', unsafe_allow_html=True)

    df_rev = pd.DataFrame(st.session_state.revenues)
    df_exp = pd.DataFrame(st.session_state.expenses)

    total_revenus = df_rev["Total Revenus"].sum() if not df_rev.empty else 0
    total_depenses = df_exp["Montant"].sum() if not df_exp.empty else 0
    revenu_net = total_revenus - total_depenses

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="metric-card metric-card-revenue"><h3>Revenus</h3><h2>{total_revenus:.2f} {currency}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card metric-card-expense"><h3>Dépenses</h3><h2>{total_depenses:.2f} {currency}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-card-balance"><h3>Solde</h3><h2>{revenu_net:.2f} {currency}</h2></div>', unsafe_allow_html=True)

# ===============================
# REVENUS
# ===============================

elif page == "💰 Revenus":
    st.markdown('<div class="big-title">💰 Gérer les Revenus</div>', unsafe_allow_html=True)

    # --- Section pour l'ajout manuel ---
    col_manual, col_import = st.columns([1, 1]) # Deux colonnes pour le layout

    with col_manual:
        st.markdown("#### Ajouter un revenu manuellement")

        salaire = st.number_input("Salaire mensuel", min_value=0.0, key="salary_input")
        revenu_sup = st.number_input("Revenus supplémentaires", min_value=0.0, key="sup_revenue_input")
        date = st.date_input("Date", key="revenue_date_input")

        if st.button("Ajouter les revenus", key="add_revenue_button"):
            st.session_state.revenues.append({
                "Date": date,
                "Salaire": salaire,
                "Revenus supplémentaires": revenu_sup,
                "Total Revenus": salaire + revenu_sup
            })
            st.success("Revenus ajoutés")

    with col_import:
        st.markdown("#### Importer des revenus (CSV)")
        uploaded_file = st.file_uploader("Choisir un fichier CSV pour les revenus", type=["csv"], key="revenue_file_uploader")

        if st.button("Importer et fusionner les revenus", key="import_merge_revenue_button"):
            if uploaded_file is not None:
                try:
                    imported_df = pd.read_csv(uploaded_file)
                    required_cols = ["Date", "Salaire", "Revenus supplémentaires", "Total Revenus"]

                    if not all(col in imported_df.columns for col in required_cols):
                        st.error(f"Le fichier CSV doit contenir les colonnes suivantes : {', '.join(required_cols)}")
                    else:
                        imported_df["Date"] = pd.to_datetime(imported_df["Date"]).dt.date

                        if st.session_state.revenues:
                            existing_df = pd.DataFrame(st.session_state.revenues)
                            updated_df = pd.concat([existing_df, imported_df], ignore_index=True)
                        else:
                            updated_df = imported_df

                        st.session_state.revenues = updated_df.to_dict('records')
                        st.success("Revenus importés et fusionnés avec succès !")
                        st.rerun()
                except Exception as e:
                    st.error(f"Une erreur est survenue lors de l'importation du fichier de revenus : {e}")
            else:
                st.warning("Veuillez d'abord télécharger un fichier CSV.")

    st.markdown("---")

    if st.session_state.revenues:
        st.markdown("#### Historique des Revenues")
        df_rev_display = pd.DataFrame(st.session_state.revenues)
        df_rev_display['Date'] = pd.to_datetime(df_rev_display['Date']).dt.date

        # Add download button for revenues
        csv_rev = df_rev_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les revenus en CSV",
            data=csv_rev,
            file_name="revenus.csv",
            mime="text/csv",
            key="download_revenue_csv"
        )

        # Display column headers
        col_header_date, col_header_salary, col_header_sup_rev, col_header_total, col_header_delete = st.columns([0.15, 0.25, 0.25, 0.25, 0.1])
        with col_header_date:
            st.write("**Date**")
        with col_header_salary:
            st.write("**Salaire**")
        with col_header_sup_rev:
            st.write("**Revenus supp.**")
        with col_header_total:
            st.write("**Total**")
        with col_header_delete:
            st.write("") # Empty header for the delete button column

        for i, row in df_rev_display.iterrows():
            col_date, col_salary, col_sup_rev, col_total, col_delete = st.columns([0.15, 0.25, 0.25, 0.25, 0.1])
            with col_date:
                st.write(row['Date'])
            with col_salary:
                st.write(f"{row['Salaire']:.2f} {currency}")
            with col_sup_rev:
                st.write(f"{row['Revenus supplémentaires']:.2f} {currency}")
            with col_total:
                st.write(f"{row['Total Revenus']:.2f} {currency}")
            with col_delete:
                if st.button("🗑️", key=f"delete_rev_{i}"):
                    if st.session_state.revenues and 0 <= i < len(st.session_state.revenues):
                        del st.session_state.revenues[i]
                        st.success("Revenu supprimé.")
                        st.rerun()
    else:
        st.info("Aucun revenu enregistré pour le moment.")

# ===============================
# DEPENSES
# ===============================

elif page == "📊 Dépenses":
    st.markdown('<div class="big-title">📊 Dépenses</div>', unsafe_allow_html=True)

    # --- Section pour l'ajout manuel ---
    col_manual, col_import = st.columns([1, 1]) # Deux colonnes pour le layout

    with col_manual:
        st.markdown("#### Ajouter une nouvelle dépense manuellement")
        categories = [
            "Logement",
            "Supermarché",
            "Transport",
            "Autres Charges",
            "Restauration & Divertissement",
            "Études",
            "Santé",
            "Epargnes",
        ]

        category = st.selectbox("Catégorie", categories, key="manual_category")
        amount = st.number_input("Montant", min_value=0.0, key="manual_amount")
        date = st.date_input("Date", key="manual_date")

        if st.button("Ajouter dépense manuelle", key="add_manual_expense"):
            st.session_state.expenses.append({
                "Date": date,
                "Catégorie": category,
                "Montant": amount
            })
            st.success("Dépense ajoutée manuellement")

    with col_import:
        st.markdown("#### Importer des dépenses (CSV)")
        uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"], key="file_uploader")

        # Bouton pour déclencher l'importation après le téléchargement du fichier
        if st.button("Importer et fusionner les dépenses", key="import_merge_button"):
            if uploaded_file is not None:
                try:
                    imported_df = pd.read_csv(uploaded_file)
                    required_cols = ["Date", "Catégorie", "Montant"]

                    # Validation des colonnes
                    if not all(col in imported_df.columns for col in required_cols):
                        st.error(f"Le fichier CSV doit contenir les colonnes suivantes : {', '.join(required_cols)}")
                    else:
                        # Convertir la colonne Date au format datetime.date pour la cohérence
                        imported_df["Date"] = pd.to_datetime(imported_df["Date"]).dt.date

                        # Fusionner avec les dépenses existantes
                        if st.session_state.expenses:
                            existing_df = pd.DataFrame(st.session_state.expenses)
                            updated_df = pd.concat([existing_df, imported_df], ignore_index=True)
                        else:
                            updated_df = imported_df

                        # Mettre à jour la session state
                        st.session_state.expenses = updated_df.to_dict('records')
                        st.success("Dépenses importées et fusionnées avec succès !")
                        st.rerun()
                except Exception as e:
                    st.error(f"Une erreur est survenue lors de l'importation du fichier : {e}")
            else:
                st.warning("Veuillez d'abord télécharger un fichier CSV.")

    st.markdown("---") # Séparateur visuel

    # --- Affichage des dépenses actuelles ---
    if st.session_state.expenses:
        st.markdown("#### Historique des Dépenses")
        df_expenses_display = pd.DataFrame(st.session_state.expenses)
        # Afficher uniquement la date pour une meilleure lisibilité
        df_expenses_display['Date'] = pd.to_datetime(df_expenses_display['Date']).dt.date

        # Add download button for expenses
        csv_exp = df_expenses_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les dépenses en CSV",
            data=csv_exp,
            file_name="depenses.csv",
            mime="text/csv",
            key="download_expense_csv"
        )

        # Display column headers
        col_header_date, col_header_category, col_header_amount, col_header_delete = st.columns([0.2, 0.3, 0.3, 0.2])
        with col_header_date:
            st.write("**Date**")
        with col_header_category:
            st.write("**Catégorie**")
        with col_header_amount:
            st.write("**Montant**")
        with col_header_delete:
            st.write("") # Empty header for the delete button column

        # Display expenses with delete buttons
        for i, row in df_expenses_display.iterrows():
            col_date, col_category, col_amount, col_delete = st.columns([0.2, 0.3, 0.3, 0.2])
            with col_date:
                st.write(row['Date'])
            with col_category:
                st.write(row['Catégorie'])
            with col_amount:
                st.write(f"{row['Montant']:.2f} {currency}")
            with col_delete:
                if st.button("🗑️", key=f"delete_exp_{i}"):
                    if st.session_state.expenses and 0 <= i < len(st.session_state.expenses):
                        del st.session_state.expenses[i]
                        st.success("Dépense supprimée.")
                        st.rerun()
    else:
        st.info("Aucune dépense enregistrée pour le moment.")

# ===============================
# ANALYSE COMPLETE
# ===============================

elif page == "📈 Analyse":
    st.markdown('<div class="big-title">📈 Analyses et synthèse</div>', unsafe_allow_html=True)

    if not st.session_state.expenses:
        st.warning("Aucune donnée disponible.")
    else:
        df = pd.DataFrame(st.session_state.expenses)
        df["Date"] = pd.to_datetime(df["Date"])

        # --- Filtres de fréquence et de période ---
        col_freq, col_period_start, col_period_end = st.columns([0.3, 0.35, 0.35])

        with col_freq:
            freq = st.selectbox(
                "Choisir la fréquence d'analyse",
                ["Journalier", "Hebdomadaire", "Mensuel", "Annuel"],
                key="analysis_frequency"
            )

        with col_period_start:
            min_date = df["Date"].min().date() if not df.empty else datetime.today().date()
            max_date = df["Date"].max().date() if not df.empty else datetime.today().date()
            start_date = st.date_input(
                "Date de début",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="analysis_start_date"
            )

        with col_period_end:
            end_date = st.date_input(
                "Date de fin",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="analysis_end_date"
            )

        # Filtrer le DataFrame par la période sélectionnée
        df_filtered = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

        if df_filtered.empty:
            st.warning("Aucune donnée disponible pour la période et la fréquence sélectionnées.")
            st.stop()

        # ===============================
        # EVOLUTION TOTALE + PAR CATEGORIE
        # ===============================

        if freq == "Journalier":
            df_filtered["Periode"] = df_filtered["Date"].dt.date
        elif freq == "Hebdomadaire":
            df_filtered["Periode"] = df_filtered["Date"].dt.to_period("W").astype(str)
        elif freq == "Mensuel":
            df_filtered["Periode"] = df_filtered["Date"].dt.to_period("M").astype(str)
        else:
            df_filtered["Periode"] = df_filtered["Date"].dt.to_period("Y").astype(str)

        # Total
        df_total = df_filtered.groupby("Periode")["Montant"].sum().reset_index()
        df_total["Type"] = "Total Dépenses"

        # Par catégorie
        df_cat = df_filtered.groupby(["Periode", "Catégorie"])["Montant"].sum().reset_index()
        df_cat.rename(columns={"Catégorie": "Type"}, inplace=True)

        # Fusion
        df_evolution = pd.concat([df_total, df_cat])

        st.markdown("## 📊 Évolution Totale et par Catégorie")

        fig_line = px.line(
            df_evolution,
            x="Periode",
            y="Montant",
            color="Type",
            markers=True,
            title=f"Évolution {freq} des Dépenses du ({start_date} à {end_date})"
        )

        fig_line.update_layout(
            legend_title="Type de Dépense",
            hovermode="x unified"
        )

        # Set traces other than 'Total Dépenses' to be 'legendonly' (hidden by default)
        for trace in fig_line.data:
            if trace.name != "Total Dépenses":
                trace.visible = "legendonly"

        st.plotly_chart(fig_line, use_container_width=True)

        # ===============================
        # DIAGRAMME CIRCULAIRE
        # ===============================

        st.markdown("## 🥧 Proportion des Dépenses")

        fig_pie = px.pie(
            df_filtered,
            names="Catégorie",
            values="Montant",
            title=f"Proportion des Dépenses par Catégorie ({start_date} à {end_date})"
        )

        st.plotly_chart(fig_pie, use_container_width=True)

        # ===============================
        # STATISTIQUES PAR CATEGORIE (incluant une ligne pour le total)
# ===============================

        st.markdown("## 📂 Statistiques par Type de Dépense")

        # Prepare aggregated data for statistics based on frequency
        if freq == "Journalier":
            # For daily, stats are on individual transactions per category
            df_aggregated_for_stats_cat = df_filtered.copy()
            df_aggregated_for_stats_total = df_filtered.copy()
        else:
            # For weekly, monthly, yearly, stats are on the sums per period
            df_aggregated_for_stats_cat = df_filtered.groupby([df_filtered["Date"].dt.to_period(freq[0]), "Catégorie"])["Montant"].sum().reset_index()
            df_aggregated_for_stats_cat["PeriodKey"] = df_aggregated_for_stats_cat["Date"].astype(str) # Convert Period object to string
            df_aggregated_for_stats_cat = df_aggregated_for_stats_cat.drop(columns="Date")

            df_aggregated_for_stats_total = df_filtered.groupby(df_filtered["Date"].dt.to_period(freq[0]))["Montant"].sum().reset_index(name="Montant")
            df_aggregated_for_stats_total["PeriodKey"] = df_aggregated_for_stats_total["Date"].astype(str) # Convert Period object to string
            df_aggregated_for_stats_total = df_aggregated_for_stats_total.drop(columns="Date")

        # Calculate category statistics on the appropriate data
        stats_cat = df_aggregated_for_stats_cat.groupby("Catégorie")["Montant"].agg(
            mean="mean",
            std="std",
            min="min",
            max="max"
        ).reset_index()

        # Calculate overall statistics for 'Total Dépenses' row
        # These stats should be on the *period sums* for the selected frequency
        overall_mean_val = df_aggregated_for_stats_total["Montant"].mean()
        overall_std_val = df_aggregated_for_stats_total["Montant"].std()
        overall_min_val = df_aggregated_for_stats_total["Montant"].min()
        overall_max_val = df_aggregated_for_stats_total["Montant"].max()

        # Handle cases where std might be NaN if only one period exists
        if pd.isna(overall_std_val):
            overall_std_val = 0.0

        total_row = pd.DataFrame([{
            "Catégorie": "Total Dépenses**", # Added bold markdown
            "mean": overall_mean_val,
            "std": overall_std_val,
            "min": overall_min_val,
            "max": overall_max_val
        }])

        # Concatenate category statistics with the total row
        stats_final = pd.concat([stats_cat, total_row], ignore_index=True)
        st.dataframe(stats_final, use_container_width=True)

# ===============================
# AI CONSEILLER
# ===============================

elif page == "🤖 AI Conseiller":
    st.markdown('<div class="big-title">🤖 AI Conseiller</div>', unsafe_allow_html=True)

    # Récupérer la clé API OpenAI depuis les variables d'environnement
    # L'utilisateur devra définir la variable d'environnement OPENAI_API_KEY.
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not st.session_state.expenses:
        st.warning("Ajoutez des dépenses pour obtenir une analyse IA.")
    elif not openai_api_key:
        st.error("Clé API OpenAI non configurée. Veuillez définir la variable d'environnement OPENAI_API_KEY.")
    else:
        df = pd.DataFrame(st.session_state.expenses)

        prompt = f"""
        Analyse de manière synthétiques les dépenses suivantes :
        {df.groupby("Catégorie")["Montant"].sum().to_dict()}
        Donne-moi des recommandations personnalisées pour optimiser mes finances, réduire les dépenses inutiles et améliorer mon épargne.
        Formule tes conseils de manière claire, concise et actionnable, en mettant l'accent sur les catégories les plus coûteuses.

        """

        if st.button("Analyser avec IA"):
            try:
                client = OpenAI(api_key=openai_api_key)

                with st.spinner("Analyse en cours..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Tu es un expert financier stratégique."},
                            {"role": "user", "content": prompt}
                        ]
                    )

                st.success("Analyse IA")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API OpenAI : {e}")
