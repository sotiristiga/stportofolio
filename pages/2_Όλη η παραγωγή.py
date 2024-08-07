import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_dynamic_filters import DynamicFilters

lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'

def metrics_customize(red, green, blue, iconname, sline, i):
    htmlstr = f"""<p style='background-color: rgb({red},{green},{blue}, 0.75); 
                        color: rgb(0,0,0, 0.75); 
                        font-size: 25px; 
                        border-radius: 7px; 
                        padding-left: 12px; 
                        padding-top: 18px; 
                        padding-bottom: 18px; 
                        line-height:25px;'>
                        <i class='{iconname} fa-xs'></i> {i}
                        </style><BR><span style='font-size: 22px; 
                        margin-top: 0;'>{sline}</style></span></p>"""
    return htmlstr


st.set_page_config(layout='wide', page_title="Όλη η παραγωγή")
ME = pd.read_csv(f"https://raw.githubusercontent.com/sotiristiga/Tiganitas_Sotiris_portofolio/main/ME_2023_2024.csv")
IM = pd.read_csv(f"https://raw.githubusercontent.com/sotiristiga/Tiganitas_Sotiris_portofolio/main/IM_2023_2024.csv")
IM['Platform'] = "Insurance Market"
ME['Platform'] = "Megabroker"
ME['District'] = ME['District'].replace("ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ", "ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑ")
ME['District'] = ME['District'].replace("ΑΤΤΙΚΗ", "ΑΤΤΙΚΗΣ")
ME['District'] = ME['District'].replace("ΚΑΛΛΙΘΕΑ", "ΑΤΤΙΚΗΣ")
IM['District']=IM['District'].replace("ΚΑΛΛΙΘΕΑ","ΑΤΤΙΚΗΣ")
ME['District'] = ME['District'].replace("ΑΧΑΪΑΣ", "ΑΧΑΙΑΣ")
ME['District'] = ME['District'].replace("ΚΟΡΙΝΘΟΥ", "ΚΟΡΙΝΘΙΑΣ")
ME['District'] = ME['District'].replace("ΛΑΡΙΣΗΣ", "ΛΑΡΙΣΑΣ")
IM['District'] = IM['District'].replace("ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ", "ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑ")
IM['District'] = IM['District'].replace("ΔΩΔΕΚΑΝΗΣΟΥ", "ΔΩΔΕΚΑΝΗΣΩΝ")
ME['District'] = ME['District'].replace("ΠΕΛΛΑΣ", "ΠΕΛΛΗΣ")
IM['District'] = IM['District'].replace("ΔΩΔΕΚΑΝΗΣΟΥ", "ΔΩΔΕΚΑΝΗΣΩΝ")
ME['District'] = ME['District'].replace("ΠΕΛΛΑΣ", "ΠΕΛΛΗΣ")
IM['Category'] = IM['Category'].replace("ΑΥΤΟΚΙΝΗΤΟ", "ΑΥΤΟΚΙΝΗΤΩΝ")
IM['Category'] = IM['Category'].replace("ΠΡΟΣΩΠΙΚΟ ΑΤΥΧΗΜΑ (ΟΧΗΜΑ)", "ΠΡΟΣΩΠΙΚΩΝ ΑΤΥΧΗΜΑΤΩΝ")
IM['Category'] = IM['Category'].replace("ΟΔΙΚΗ ΒΟΗΘΕΙΑ", "ΟΔΙΚΗΣ ΒΟΗΘΕΙΑΣ")
IM['Category'] = IM['Category'].replace("ΝΟΜΙΚΗ ΠΡΟΣΤΑΣΙΑ", "ΝΟΜΙΚΗΣ ΠΡΟΣΤΑΣΙΑΣ")
IM['Category'] = IM['Category'].replace("ΣΚΑΦΗ", "ΣΚΑΦΩΝ")
IM_select = IM[
    ['N_Policy', 'Company', 'Category', 'Char', 'Started', 'Expired', 'District', 'Gross', 'Net', 'Commissions', 'id',
     'Platform']]

All = pd.concat([ME, IM_select])
All['District'].value_counts().reset_index().sort_values('District')
All['Started'] = pd.to_datetime(All['Started'], dayfirst=True)
All['Expired'] = pd.to_datetime(All['Expired'], dayfirst=True)

All['Year'] = All['Started'].dt.year
All['Year'] = pd.Categorical(All['Year'], categories=pd.Series([2023, 2024]))
month_levels = pd.Series([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

All['Month'] = All['Started'].dt.month_name()

All['Month'] = pd.Categorical(All['Month'], categories=month_levels)

All['Month_Year'] = All["Started"].dt.strftime('%m-%Y')


def duration_groups(duration):
    if duration == 1:
        return "Μηνιαίο"
    elif duration == 3:
        return "Τρίμηνο"
    elif duration == 6:
        return "Εξάμηνο"
    elif duration == 12:
        return "Ετήσιο"
    else:
        return "Άλλη"


All['Duration'] = (
            (All['Expired'].dt.year - All['Started'].dt.year) * 12 + All['Expired'].dt.month - All['Started'].dt.month +
            All['Expired'].dt.day / 30 - All['Started'].dt.day / 30).round(0)
All['Duration_gr'] = All['Duration'].apply(duration_groups)
duration_levels = pd.Series(["Ετήσιο", "Εξάμηνο", "Τρίμηνο", "Μηνιαίο", "Άλλη"])
All['Duration_gr'] = pd.Categorical(All['Duration_gr'], categories=duration_levels)

dynamic_filters = DynamicFilters(All, filters=['Year', 'Month'])

with st.sidebar:
    dynamic_filters.display_filters()

All1 = dynamic_filters.filter_df()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-users", "Πελάτες", All1['id'].nunique()),
                unsafe_allow_html=True)

with kpi2:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-file-contract", "Συμβόλαια", All1['N_Policy'].nunique()),
                unsafe_allow_html=True)

with kpi3:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Καθαρά Ασφάλιστρα", All1['Net'].sum().round(2)),
        unsafe_allow_html=True)
with kpi4:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Προμήθειες", All1['Commissions'].sum().round(2)),
        unsafe_allow_html=True)

with kpi5:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-percent", "Ποσοστό Προμήθειας",
                                        ((All1['Commissions'].sum() / All1['Net'].sum()).round(3) * 100)),
                unsafe_allow_html=True)

pie1, pie2, pie3, pie4 = st.columns(4)
with pie1:
    pie1 = px.pie(All1[['N_Policy', 'Platform']].value_counts().reset_index().groupby('Platform').count().reset_index(),
                  values='count', names='Platform', color='Platform',
                  color_discrete_sequence=px.colors.sequential.Viridis_r, labels={'count': 'Σύνολο',
                                                                                  'Platform': 'Πλατφόρμα'},
                  height=350,
                  title='Πελάτες<br>(ανά πλατφόρμα)', hole=0.5, width=150)
    pie1.update_traces(hoverinfo="value", textfont_size=17)
    pie1.update_layout(plot_bgcolor='white', font_size=20,
                       legend=dict(yanchor="top", y=0.04, xanchor="left", x=0.00005), legend_title_text='Πλατφόρμα',
                       title_x=0.1, title_y=0.8)
    st.write(pie1)

with pie2:
    pie2 = px.pie(All1[['id', 'Platform']].value_counts().reset_index().groupby('Platform').count().reset_index(),
                  values='count', names='Platform', color='Platform',
                  color_discrete_sequence=px.colors.sequential.Viridis_r, labels={'count': 'Σύνολο',
                                                                                  'Platform': 'Πλατφόρμα'},
                  height=350,
                  title='Συμβόλαια<br>(ανά πλατφόρμα)', hole=0.5, width=150)
    pie2.update_traces(hoverinfo="value", textfont_size=17)
    pie2.update_layout(plot_bgcolor='white', font_size=20, showlegend=False, title_y=0.8)
    st.write(pie2)

with pie3:
    pie3 = px.pie(All1.groupby('Platform')['Net'].sum().reset_index(),
                  values='Net', names='Platform', color='Platform',
                  color_discrete_sequence=px.colors.sequential.Viridis_r, labels={'Net': 'Καθαρά<br>ασφάλιστρα',
                                                                                  'Platform': 'Πλατφόρμα'},
                  height=350,
                  title='Καθαρά<br>ασφάλιστρα <br>(ανά πλατφόρμα)', hole=0.5, width=150)
    pie3.update_traces(hoverinfo="value", textfont_size=17)
    pie3.update_layout(plot_bgcolor='white', font_size=20,
                       showlegend=False, title_x=0.1, title_y=0.85)
    st.write(pie3)

with pie4:
    pie4 = px.pie(All1.groupby('Platform')['Commissions'].sum().reset_index(),
                  values='Commissions', names='Platform', color='Platform',
                  color_discrete_sequence=px.colors.sequential.Viridis_r, labels={'Commissions': 'Προμήθειες',
                                                                                  'Platform': 'Πλατφόρμα'},
                  height=350,
                  title='Προμήθειες<br>(ανά πλατφόρμα)', hole=0.5, width=150)
    pie4.update_traces(hoverinfo="value", textfont_size=17)
    pie4.update_layout(plot_bgcolor='white', font_size=20, showlegend=False, title_x=0.1, title_y=0.8)
    st.write(pie4)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Παραγωγή ανά εταιρεια", "Παραγωγή ανά κλάδο", "Εξέλιξη Παραγωγής", "Δημογραφικά Πελατών", 'Διάρκειες Συμβολαίων'])
with tab1:
    tab11, tab12, tab13, tab14 = st.tabs(
        ["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες", "Ανά εταιρεία σε κάθε πλατφόρμα"])
    with tab11:
        companies_countpol = All1['Company'].value_counts().reset_index()
        fig_barplot = px.bar(companies_countpol.sort_values("count"), x='count', y='Company', title='',
                             labels={'count': 'Σύνολο Συμβολαίων', 'Company': 'Ασφ. Εταιρεία'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text_auto=True,
                             height=1000)
        fig_barplot.update_traces(textfont_size=17, textangle=0.5, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)

    with tab12:
        companies_net = All1.groupby('Company')['Net'].sum().reset_index()
        companies_net_sorted = companies_net.sort_values('Net', ascending=True)
        fig_barplot_net1 = px.bar(companies_net_sorted, x='Net', y='Company', title='',
                                  labels={'Net': 'Καθαρά €', 'Company': 'Ασφ. Εταιρεία'},
                                  color_discrete_sequence=px.colors.sequential.Blugrn,
                                  text='Net', height=1000)
        fig_barplot_net1.update_traces(textfont_size=17, texttemplate='%{text:.2s} €',
                                       textangle=0, textposition="outside", cliponaxis=False)
        fig_barplot_net1.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot_net1)

    with tab13:
        companies_comm = All1.groupby('Company')['Commissions'].sum().reset_index()
        companies_comm_sorted = companies_comm.sort_values('Commissions', ascending=True)
        fig_barplot = px.bar(companies_comm_sorted, x='Commissions', y='Company', title='',
                             labels={'Commissions': 'Προμήθειες €', 'Company': 'Ασφ. Εταιρεία'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text='Commissions', height=1000, width=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €', textangle=0, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab14:
        option1 = st.selectbox("Ασφαλιστική Εταιρεία", pd.unique(companies_countpol['Company']))

        col11, col12, col13 = st.columns(3)
        with col11:
            companies_countpol = All1[['Company', "Platform"]].value_counts().reset_index().sort_values('Company')
            fig_barplot = px.bar(companies_countpol[companies_countpol['Company'] == option1], x='Platform', y='count',
                                 title='Συμβόλαια',
                                 color="Platform",
                                 text_auto=True,
                                 labels={'count': 'Σύνολο Συμβολαίων', 'Company': 'Ασφ. Εταιρεία',
                                         "Platform": 'Πλατφορμα'},
                                 color_discrete_sequence=px.colors.sequential.Blugrn,
                                 height=700, width=500)
            fig_barplot.update_traces(textfont_size=25, textangle=0.5, textposition="outside",
                                      cliponaxis=False)
            fig_barplot.update_xaxes(categoryorder="total ascending")
            fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_barplot)
        with col12:
            companies_net = All1.groupby(['Company', "Platform"])['Net'].sum().reset_index()
            fig_barplot_net2 = px.bar(companies_net[companies_net['Company'] == option1], x='Platform', y='Net',
                                      title='Καθαρά €',
                                      color="Platform",
                                      text='Net',
                                      labels={'Net': 'Καθαρά €', 'Company': 'Ασφ. Εταιρεία', "Platform": 'Πλατφορμα'},
                                      color_discrete_sequence=px.colors.sequential.Blugrn,
                                      height=700, width=1000)
            fig_barplot_net2.update_traces(textfont_size=25, textangle=0.5, texttemplate='%{text:.3s} €',
                                           textposition="outside",
                                           cliponaxis=False)
            fig_barplot_net2.update_xaxes(categoryorder="total ascending")
            fig_barplot_net2.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_barplot_net2)

        with col13:
            companies_com = All1.groupby(['Company', "Platform"])['Commissions'].sum().reset_index()
            fig_barplot_com2 = px.bar(companies_com[companies_com['Company'] == option1], x='Platform', y='Commissions',
                                      title='Προμήθειες €',
                                      color="Platform",
                                      text='Commissions',
                                      labels={'Commissions': 'Προμήθειες €', 'Company': 'Ασφ. Εταιρεία',
                                              "Platform": 'Πλατφορμα'},
                                      color_discrete_sequence=px.colors.sequential.Blugrn,
                                      height=700, width=1000)
            fig_barplot_com2.update_traces(textfont_size=25, textangle=0.5, texttemplate='%{text:.2s} €',
                                           textposition="outside",
                                           cliponaxis=False)
            fig_barplot_com2.update_xaxes(categoryorder="total ascending")
            fig_barplot_com2.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_barplot_com2)

with tab2:
    tab21, tab22, tab23, tab24 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες", "Ανά κλάδο σε κάθε πλατφόρμα"])
    with tab21:
        categories_countpol = All1['Category'].value_counts().reset_index()
        fig_barplot = px.bar(categories_countpol.sort_values("count"), x='count', y='Category', title='',
                             labels={'count': 'Σύνολο Συμβολαίων', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text_auto=True, height=1000)
        fig_barplot.update_traces(textfont_size=17, textangle=0, textposition="outside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab22:
        categories_net = All1.groupby('Category')['Net'].sum().reset_index()
        categories_net_sorted = categories_net.sort_values('Net', ascending=True)
        fig_barplot = px.bar(categories_net_sorted, x='Net', y='Category', title='',
                             labels={'Net': 'Καθαρά €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Net', width=1000, height=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab23:
        categories_comm = All1.groupby('Category')['Commissions'].sum().reset_index()
        categories_comm_sorted = categories_comm.sort_values('Commissions', ascending=True)
        fig_barplot = px.bar(categories_comm_sorted, x='Commissions', y='Category', title='',
                             labels={'Commissions': 'Προμήθειες €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Commissions', width=1000,
                             height=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €', textangle=0,
                                  textposition="outside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab24:
        Category_countpol = All1[['Category', "Platform"]].value_counts().reset_index().sort_values('Category')
        option2 = st.selectbox("Κλάδος", pd.unique(Category_countpol['Category']))
        col21, col22, col23 = st.columns(3)
        with col21:
            fig_barplot = px.bar(Category_countpol[Category_countpol['Category'] == option2], x='Platform', y='count',
                                 title="Συμβόλαια",
                                 color="Platform",
                                 text_auto=True,
                                 labels={'count': 'Σύνολο Συμβολαίων', 'Category': 'Κλάδος', "Platform": 'Πλατφορμα'},
                                 color_discrete_sequence=px.colors.sequential.Blugrn,
                                 height=700, width=500)
            fig_barplot.update_traces(textfont_size=25, textangle=0.5, textposition="outside",
                                      cliponaxis=False)
            fig_barplot.update_xaxes(categoryorder="total ascending")
            fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_barplot)
        with col22:
            Category_net = All1.groupby(['Category', "Platform"])['Net'].sum().reset_index()
            Category_net2 = px.bar(Category_net[Category_net['Category'] == option2], x='Platform', y='Net',
                                   title="Καθαρά €",
                                   color="Platform",
                                   text="Net",
                                   labels={'Net': 'Καθαρά €', 'Category': 'Κλάδος', "Platform": 'Πλατφορμα'},
                                   color_discrete_sequence=px.colors.sequential.Blugrn,
                                   height=700, width=500)
            Category_net2.update_traces(textfont_size=25, textangle=0.5, texttemplate='%{text:.3s} €',
                                        textposition="outside",
                                        cliponaxis=False)
            Category_net2.update_xaxes(categoryorder="total ascending")
            Category_net2.update_layout(plot_bgcolor='white', font_size=15)
            st.write(Category_net2)

        with col23:
            Category_com = All1.groupby(['Category', "Platform"])['Commissions'].sum().reset_index()
            Category_com2 = px.bar(Category_com[Category_com['Category'] == option2], x='Platform', y='Commissions',
                                   title='Προμήθειες €',
                                   color="Platform",
                                   text='Commissions',
                                   labels={'Commissions': 'Προμήθειες €', 'Category': 'Κλάδος',
                                           "Platform": 'Πλατφορμα'},
                                   color_discrete_sequence=px.colors.sequential.Blugrn,
                                   height=700, width=500)
            Category_com2.update_traces(textfont_size=25, textangle=0.5, texttemplate='%{text:.3s} €',
                                        textposition="outside",
                                        cliponaxis=False)
            Category_com2.update_xaxes(categoryorder="total ascending")
            Category_com2.update_layout(plot_bgcolor='white', font_size=15)
            st.write(Category_com2)

with tab3:
    prod_line_by_month = All1.groupby('Month_Year')[['Commissions', "Net"]].sum().reset_index()
    prod_line_by_month['Month_Year'] = pd.to_datetime(prod_line_by_month['Month_Year'], format='mixed')
    prod_line_by_month = prod_line_by_month.sort_values('Month_Year', ascending=False)
    prod_line_by_month_count = All1['Month_Year'].value_counts().reset_index()
    prod_line_by_month_count['Month_Year'] = pd.to_datetime(prod_line_by_month_count['Month_Year'], format='mixed')
    prod_line_by_month_count = prod_line_by_month_count.sort_values('Month_Year', ascending=False)
    prod_line_by_month['Year'] = prod_line_by_month['Month_Year'].dt.year
    prod_line_by_month['Month'] = prod_line_by_month['Month_Year'].dt.month_name()
    prod_line_by_month_mean = prod_line_by_month.groupby('Month')[['Commissions', "Net"]].mean().round(1).reset_index()
    prod_line_by_month_mean['Month'] = pd.Categorical(prod_line_by_month_mean['Month'], categories=month_levels)
    prod_line_by_month_count['Year'] = prod_line_by_month_count['Month_Year'].dt.year
    prod_line_by_month_count['Month'] = prod_line_by_month_count['Month_Year'].dt.month_name()
    prod_line_by_month_mean_count = prod_line_by_month_count.groupby('Month')['count'].mean().reset_index()
    prod_line_by_month_mean_count['Month'] = pd.Categorical(prod_line_by_month_mean_count['Month'],
                                                            categories=month_levels)
    prod_line_by_year = prod_line_by_month.groupby('Year')[['Commissions', "Net"]].sum().reset_index()
    prod_line_by_year_count = prod_line_by_month_count.groupby('Year')['count'].sum().reset_index()
    prod_line_by_year_count['Year'] = pd.Categorical(prod_line_by_year_count['Year'], pd.Series([2023, 2024]))
    tab31, tab32, tab33 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες"])
    with tab31:
        tabs311, tabs312 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs311:
            fig_line_polcou = px.bar(prod_line_by_year_count,
                                     x="Year", y="count",
                                     title='Σύνολο συμβολαίων ανά έτος απο το 2020 έως 2023',
                                     color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                     labels={'count': 'Σύνολο συμβολαίων', 'Year': 'Έτος'}, width=500, text_auto=True)
            fig_line_polcou.update_traces(textfont_size=17, textangle=0,
                                          textposition="outside", cliponaxis=False)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_line_polcou)
        with tabs312:
            plat_count_by_year = All1[["Year", "Platform"]].value_counts().reset_index()
            plat_count_by_year_bar = px.bar(plat_count_by_year,
                                            x="Year", y="count", color="Platform", barmode="group",
                                            title='Σύνολο συμβολαίων ανά έτος',
                                            color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                            labels={'count': 'Σύνολο συμβολαίων', 'Year': 'Έτος',
                                                    'Platform': 'Πλατφόρμα'}, width=900, text_auto=True)
            plat_count_by_year_bar.update_traces(textfont_size=17, textangle=0,
                                                 textposition="outside", cliponaxis=False)
            plat_count_by_year_bar.update_layout(plot_bgcolor='white', font_size=15)
            st.write(plat_count_by_year_bar)
        tabs313, tabs314 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs313:
            fig_line_polcou = px.line(prod_line_by_month_count,
                                      x="Month_Year", y="count",
                                      title='Σύνολο συμβολαίων ανά μήνα',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'count': 'Σύνολο συμβολαίων', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)
        with tabs314:
            plat_count_by_year = All1[["Month_Year", "Platform"]].value_counts().reset_index()
            plat_count_by_year['Month_Year'] = pd.to_datetime(plat_count_by_year['Month_Year'], format='mixed')
            plat_count_by_year = plat_count_by_year.sort_values('Month_Year')
            fig_line_plat_count_by_year = px.line(plat_count_by_year,
                                                  x="Month_Year", y="count", color='Platform',
                                                  title='Σύνολο συμβολαίων ανά μήνα',
                                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                                  labels={'count': 'Σύνολο συμβολαίων', 'Month_Year': 'Μήνας-Έτος',
                                                          'Platform': 'Πλατφόρμα'}, markers=True)
            fig_line_plat_count_by_year.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_plat_count_by_year)
        tabs315, tabs316 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs315:
            fig_line_polcou = px.line(prod_line_by_month_mean_count.sort_values('Month'),
                                      x="Month", y="count",
                                      title='Σύνολο συμβολαίων ανά μήνα',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'count': 'Σύνολο συμβολαίων', 'Month': 'Μήνας'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)

        with tabs316:
            plat_count_by_month = \
            All1[["Month_Year", "Month", "Platform"]].value_counts().reset_index().groupby(["Month", "Platform"])[
                'count'].mean().reset_index()
            plat_count_by_month = plat_count_by_month.sort_values('Month')
            fig_line_plat_count_by_month = px.line(plat_count_by_month,
                                                   x="Month", y="count", color='Platform',
                                                   title='Σύνολο συμβολαίων ανά μήνα',
                                                   color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                                   labels={'count': 'Σύνολο συμβολαίων', 'Month': 'Μήνας',
                                                           'Platform': 'Πλατφόρμα'}, markers=True)
            fig_line_plat_count_by_month.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_plat_count_by_month)

    plat_sum_by_year = All1.groupby(["Year", "Platform"])[['Net', 'Commissions']].sum().reset_index()
    plat_monthyear_sum = All1.groupby(["Month_Year", "Platform"])[['Net', 'Commissions']].sum().reset_index()
    plat_monthyear_sum['Month_Year'] = pd.to_datetime(plat_monthyear_sum['Month_Year'], format='mixed')
    plat_monthyear_sum = plat_monthyear_sum.sort_values('Month_Year')
    plat_month_mean = All1.groupby(['Month_Year', "Platform"])[['Net', 'Commissions']].sum().reset_index()
    plat_month_mean['Month_Year'] = pd.to_datetime(plat_month_mean['Month_Year'], format='mixed')
    plat_month_mean['Month'] = plat_month_mean['Month_Year'].dt.month_name()
    plat_month_mean['Month'] = pd.Categorical(plat_month_mean['Month'], categories=month_levels)
    plat_month_mean = plat_month_mean.groupby(["Month", 'Platform'])[['Net', 'Commissions']].mean().reset_index()
    plat_month_mean = plat_month_mean.sort_values('Month')
    with tab32:
        tabs321, tabs322 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs321:
            fig_line_polcou = px.bar(prod_line_by_year,
                                     x="Year", y="Net",
                                     title='Καθαρά ασφάλιστρα ανά έτος',
                                     color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                     labels={'Net': 'Καθαρά €', 'Year': 'Έτος'}, width=500, text='Net')
            fig_line_polcou.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                          textposition="outside", cliponaxis=False)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_line_polcou)
        with tabs322:
            plat_sum_by_year_net = px.bar(plat_sum_by_year,
                                          x="Year", y="Net", color='Platform', barmode='group',
                                          title='Καθαρά ασφάλιστρα ανά έτος',
                                          color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                          labels={'Net': 'Καθαρά €', 'Year': 'Έτος', 'Platform': 'Πλατφόρμα'},
                                          width=1000, text='Net')
            plat_sum_by_year_net.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                               textposition="outside", cliponaxis=False)
            plat_sum_by_year_net.update_layout(plot_bgcolor='white', font_size=15)
            st.write(plat_sum_by_year_net)

        tabs323, tabs324 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs323:
            fig_line_net = px.line(prod_line_by_month,
                                   x="Month_Year", y="Net",
                                   title='Κάθαρα Ασφάλιστρα ανά μήνα ',
                                   color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                   labels={'Net': 'Καθαρά €', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
            fig_line_net.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_net)

        with tabs324:
            plat_monthyear_sum_net = px.line(plat_monthyear_sum,
                                             x="Month_Year", y="Net", color='Platform',
                                             title='Κάθαρα Ασφάλιστρα ανά μήνα ',
                                             color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                             labels={'Net': 'Καθαρά €', 'Month_Year': 'Μήνας-Έτος',
                                                     'Platform': 'Πλατφόρμα'}, markers=True)
            plat_monthyear_sum_net.update_layout(plot_bgcolor='white', font_size=13)
            st.write(plat_monthyear_sum_net)

        tabs325, tabs326 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs325:
            fig_line_polcou = px.line(prod_line_by_month_mean.sort_values('Month'),
                                      x="Month", y="Net",
                                      title='Μέσος όρος καθαρών ασφαλίστρων ανά μήνα',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'Net': 'Καθαρά €', 'Month': 'Μήνας'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)
        with tabs326:
            plat_month_mean_net = px.line(plat_month_mean,
                                          x="Month", y="Net", color='Platform',
                                          title='Μέσος όρος καθαρών ασφαλίστρων ανά μήνα',
                                          color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                          labels={'Net': 'Καθαρά €', 'Month': 'Μήνας', 'Platform': 'Πλατφόρμα'},
                                          markers=True)
            plat_month_mean_net.update_layout(plot_bgcolor='white', font_size=13)
            st.write(plat_month_mean_net)

    with tab33:
        tabs331, tabs332 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs331:
            fig_line_polcou = px.bar(prod_line_by_year,
                                     x="Year", y="Commissions",
                                     title='Προμήθειες ανά έτος',
                                     color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                     labels={'Commissions': 'Προμήθειες €', 'Year': 'Έτος'}, width=500,
                                     text='Commissions')
            fig_line_polcou.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                          textposition="outside", cliponaxis=False)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_line_polcou)
        with tabs332:
            plat_sum_by_year_com = px.bar(plat_sum_by_year,
                                          x="Year", y="Commissions", color='Platform', barmode='group',
                                          title='Προμήθειες ανά έτος',
                                          color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                          labels={'Commissions': 'Προμήθειες €', 'Year': 'Έτος',
                                                  'Platform': 'Πλατφόρμα'}, width=1000, text='Commissions')
            plat_sum_by_year_com.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                               textposition="outside", cliponaxis=False)
            plat_sum_by_year_com.update_layout(plot_bgcolor='white', font_size=15)
            st.write(plat_sum_by_year_com)
        tabs333, tabs334 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs333:
            fig_line_com = px.line(prod_line_by_month,
                                   x="Month_Year", y="Commissions",
                                   title='Προμήθειες ανά μήνα',
                                   color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                   labels={'Commissions': 'Προμήθειες €', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
            fig_line_com.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_com)

        with tabs334:
            plat_monthyear_sum_com = px.line(plat_monthyear_sum,
                                             x="Month_Year", y="Commissions", color='Platform',
                                             title='Προμήθειες ανά μήνα ',
                                             color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                             labels={'Commissions': 'Προμήθειες €', 'Month_Year': 'Μήνας-Έτος',
                                                     'Platform': 'Πλατφόρμα'}, markers=True)
            plat_monthyear_sum_net.update_layout(plot_bgcolor='white', font_size=13)
            st.write(plat_monthyear_sum_com)
        tabs335, tabs336 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
        with tabs335:
            fig_line_polcou = px.line(prod_line_by_month_mean.sort_values('Month'),
                                      x="Month", y="Commissions",
                                      title='Μέσος όρος προμηθειών ανά μήνα',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'Commissions': 'Προμήθειες €', 'Month': 'Μήνας'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)
        with tabs336:
            plat_month_mean_net = px.line(plat_month_mean,
                                          x="Month", y="Commissions", color='Platform',
                                          title='Μέσος όρος προμηθειών ανά μήνα',
                                          color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                          labels={'Commissions': 'Προμήθειες €', 'Month': 'Μήνας',
                                                  'Platform': 'Πλατφόρμα'}, markers=True)
            plat_month_mean_net.update_layout(plot_bgcolor='white', font_size=13)
            st.write(plat_month_mean_net)

with tab4:
    st.write("# Νομός")
    discrict_data = All1.groupby(['id', 'District'])[['Gross', 'Net', 'Commissions']].sum().reset_index()
    discrict_data_total = All1.groupby(['District'])[['Gross', 'Net', 'Commissions']].sum().reset_index()
    discrictcount = discrict_data['District'].value_counts().reset_index().sort_values('count')
    fig_barplot_reg = px.bar(discrictcount, x='count', y='District', title='',
                                 labels={'count': 'Αρ. Πελατών', 'District': 'Νομός'},
                                 color_discrete_sequence=px.colors.sequential.Blugrn,
                                 text_auto=True, width=1000, height=400)
    fig_barplot_reg.update_traces(textfont_size=14, textangle=0.5, textposition="outside", cliponaxis=False)
    fig_barplot_reg.update_layout(plot_bgcolor='white', font_size=25)
    st.write(fig_barplot_reg)




with tab5:
    select_durations = All1.loc[
        (All1['Duration'] == 1) | (All1['Duration'] == 3) | (All1['Duration'] == 6) | (All1['Duration'] == 12)]
    select_duration_total_year =(select_durations[['Duration_gr', 'Month', 'Year']].value_counts().reset_index()).groupby(['Year', "Duration_gr"])[
        'count'].sum().round(1).reset_index()
    tabs51, tabs52 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
    with tabs51:
        fig_dur_bar = px.bar(select_duration_total_year.loc[select_duration_total_year['Duration_gr'] != "Άλλη"],
                             x="Year", y="count",
                             title='Χρονικές διάρκειες συμβολαίων ανά έτος (Συνολικά)', color='Duration_gr',
                             color_discrete_sequence=px.colors.sequential.Aggrnyl,
                             labels={'count': '# Συμβολαίων', 'Year': 'Έτος', "Duration_gr": 'Διάρκεια συμβολαίου'},
                             width=900, text='count', height=800)
        fig_dur_bar.update_traces(textfont_size=17, textangle=0, textposition="outside", cliponaxis=False)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
    with tabs52:
        select_duration_total_year_plat = select_durations[
            ['Duration_gr', 'Platform', 'Year']].value_counts().reset_index()
        fig_dur_bar = px.bar(
            select_duration_total_year_plat.loc[select_duration_total_year_plat['Duration_gr'] != "Άλλη"],
            x="Platform", y="count", facet_col='Year', facet_col_wrap=5,
            title='Χρονικές διάρκειες συμβολαίων ανά έτος (Συνολικά)', color='Duration_gr',
            color_discrete_sequence=px.colors.sequential.Aggrnyl,
            labels={'count': '# Συμβολαίων', 'Year': 'Έτος', "Duration_gr": 'Διάρκεια συμβολαίου',
                    'Platform': 'Πλατφόρμα'},
            width=1200, text='count', height=1000)
        fig_dur_bar.update_traces(textfont_size=17, textangle=0, textposition="outside", cliponaxis=False)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
    tabs53, tabs54 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
    with tabs53:
        select_duration_total = select_durations[['Duration_gr', 'Month']].value_counts().reset_index().sort_values(
            ['Duration_gr', 'Month'])
        fig_dur_bar = px.bar(select_duration_total,
                             x="Month", y="count",
                             title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Συνολικά)', color='Duration_gr',
                             color_discrete_sequence=px.colors.sequential.Aggrnyl,
                             labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου'},
                             width=1000, text='count')
        fig_dur_bar.update_traces(textfont_size=17, textangle=0, cliponaxis=False)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
    with tabs54:
        select_duration_total_plat = select_durations[
            ['Duration_gr', 'Platform', 'Month']].value_counts().reset_index().sort_values(['Duration_gr', 'Month'])
        fig_dur_bar = px.bar(select_duration_total_plat,
                             x="Platform", y="count", facet_col='Month', facet_col_wrap=6,
                             title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Συνολικά)', color='Duration_gr',
                             color_discrete_sequence=px.colors.sequential.Aggrnyl,
                             labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου',
                                     'Platform': 'Πλατφόρμα'},
                             width=1500, text='count', height=1200)
        fig_dur_bar.update_traces(textfont_size=17, textangle=0, cliponaxis=False)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
    tabs55, tabs56 = st.tabs(["Σύνολικα", "Σύγκριση ανά πλατφόρμα"])
    with tabs55:
        select_duration_mean = (select_durations[['Duration_gr', 'Month', 'Year']].value_counts().reset_index()).groupby(
            ['Month', "Duration_gr"])['count'].mean().round(1).reset_index()
        fig_dur_bar = px.line(select_duration_mean.loc[select_duration_mean['Duration_gr'] != "Άλλη"],
                              x="Month", y="count",
                              title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Μέσος όρος)', color='Duration_gr',
                              color_discrete_sequence=px.colors.sequential.Aggrnyl,
                              labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου'},
                              width=1000, height=1000, markers=True)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
    with tabs56:
        select_duration_mean = \
        (select_durations[['Duration_gr', 'Month', 'Platform']].value_counts().reset_index()).groupby(
            ['Month', "Duration_gr", 'Platform'])['count'].mean().round(1).reset_index()
        fig_dur_bar = px.line(select_duration_mean.loc[select_duration_mean['Duration_gr'] != "Άλλη"],
                              x="Month", y="count", facet_col='Platform', facet_col_wrap=2,
                              title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Μέσος όρος)', color='Duration_gr',
                              color_discrete_sequence=px.colors.sequential.Aggrnyl,
                              labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου',
                                      'Platform': 'Πλατφόρμα'},
                              width=2000, height=1000, markers=True)
        fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_dur_bar)
