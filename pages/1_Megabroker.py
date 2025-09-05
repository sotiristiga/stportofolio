import sys
import os

# Allow Python to find auth.py in the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth import check_login

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


st.set_page_config(layout='wide', page_title="Megabroker")

ME = pd.read_csv(f"https://raw.githubusercontent.com/sotiristiga/Tiganitas_Sotiris_portofolio/main/ME_2023_2024.csv")

ME['Started'] = pd.to_datetime(ME['Started'], dayfirst=True)
ME['Expired'] = pd.to_datetime(ME['Expired'], dayfirst=True)

ME['Year'] = ME['Started'].dt.year
ME['Year'] = pd.Categorical(ME['Year'], categories=pd.Series([2023, 2024]))
month_levels = pd.Series([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

ME['Month'] = ME['Started'].dt.month_name()

ME['Month'] = pd.Categorical(ME['Month'], categories=month_levels)

ME['Month_Year'] = ME["Started"].dt.strftime('%m-%Y')


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


ME['Duration'] = (
            (ME['Expired'].dt.year - ME['Started'].dt.year) * 12 + ME['Expired'].dt.month - ME['Started'].dt.month + ME[
        'Expired'].dt.day / 30 - ME['Started'].dt.day / 30).round(0)
ME['Duration_gr'] = ME['Duration'].apply(duration_groups)
duration_levels = pd.Series(["Ετήσιο", "Εξάμηνο", "Τρίμηνο", "Μηνιαίο", "Άλλη"])
ME['Duration_gr'] = pd.Categorical(ME['Duration_gr'], categories=duration_levels)
ME['District'] = ME['District'].replace("ΑΙΤΩΛΟΚΑΡΝΑΝΙΑ", "ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑ")
ME['District'] = ME['District'].replace("ΑΤΤΙΚΗ", "ΑΤΤΙΚΗΣ")
ME['District'] = ME['District'].replace("ΑΧΑΪΑΣ", "ΑΧΑΙΑΣ")
ME['District'] = ME['District'].replace("ΚΟΡΙΝΘΟΥ", "ΚΟΡΙΝΘΙΑΣ")
ME['District'] = ME['District'].replace("ΛΑΡΙΣΗΣ", "ΛΑΡΙΣΑΣ")
ME['District'] = ME['District'].replace("ΠΕΛΛΑΣ", "ΠΕΛΛΗΣ")
dynamic_filters = DynamicFilters(ME, filters=['Year', 'Month'])

with st.sidebar:
    dynamic_filters.display_filters()

ME1 = dynamic_filters.filter_df()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-users", "Πελάτες", ME1['id'].nunique()),
                unsafe_allow_html=True)

with kpi2:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-file-contract", "Συμβόλαια", ME1['N_Policy'].nunique()),
                unsafe_allow_html=True)

with kpi3:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Καθαρά Ασφάλιστρα", ME1['Net'].sum().round(2)),
        unsafe_allow_html=True)
with kpi4:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Προμήθειες", ME1['Commissions'].sum().round(2)),
        unsafe_allow_html=True)

with kpi5:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-percent", "Ποσοστό Προμήθειας",
                                        ((ME1['Commissions'].sum() / ME1['Net'].sum()).round(4) * 100)),
                unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Παραγωγή ανά εταιρεια", "Παραγωγή ανά κλάδο", "Εξέλιξη Παραγωγής", "Δημογραφικά Πελατών", 'Διάρκειες Συμβολαίων'])
with tab1:
    tab11, tab12, tab13 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες"])
    with tab11:
        companies_countpol = ME1['Company'].value_counts().reset_index()
        fig_barplot = px.bar(companies_countpol.sort_values("count"), x='count', y='Company', title='',
                             labels={'count': 'Σύνολο Συμβολαίων', 'Company': 'Ασφ. Εταιρεία'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text_auto=True,
                             height=1000)
        fig_barplot.update_traces(textfont_size=17, textangle=0.5, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab12:
        companies_net = ME1.groupby('Company')['Net'].sum().reset_index()
        companies_net_sorted = companies_net.sort_values('Net', ascending=True)
        fig_barplot = px.bar(companies_net_sorted, x='Net', y='Company', title='',
                             labels={'Net': 'Καθαρά €', 'Company': 'Ασφ. Εταιρεία'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text='Net', height=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €',
                                  textangle=0, textposition="outside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab13:
        companies_comm = ME1.groupby('Company')['Commissions'].sum().reset_index()
        companies_comm_sorted = companies_comm.sort_values('Commissions', ascending=True)
        fig_barplot = px.bar(companies_comm_sorted, x='Commissions', y='Company', title='',
                             labels={'Commissions': 'Προμήθειες €', 'Company': 'Ασφ. Εταιρεία'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text='Commissions', height=1000, width=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €', textangle=0, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
with tab2:
    tab21, tab22, tab23 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες"])
    with tab21:
        categories_countpol = ME1['Category'].value_counts().reset_index()
        fig_barplot = px.bar(categories_countpol.sort_values("count"), x='count', y='Category', title='',
                             labels={'count': 'Σύνολο Συμβολαίων', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text_auto=True)
        fig_barplot.update_traces(textfont_size=17, textangle=0, textposition="outside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab22:
        categories_net = ME1.groupby('Category')['Net'].sum().reset_index()
        categories_net_sorted = categories_net.sort_values('Net', ascending=True)
        fig_barplot = px.bar(categories_net_sorted, x='Net', y='Category', title='',
                             labels={'Net': 'Καθαρά €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Net', width=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0, textposition="outside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with tab23:
        categories_comm = ME1.groupby('Category')['Commissions'].sum().reset_index()
        categories_comm_sorted = categories_comm.sort_values('Commissions', ascending=True)
        fig_barplot = px.bar(categories_comm_sorted, x='Commissions', y='Category', title='',
                             labels={'Commissions': 'Προμήθειες €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Commissions', width=1000)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €', textangle=0,
                                  textposition="outside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
with tab3:
    prod_line_by_month = ME1.groupby('Month_Year')[['Commissions', "Net"]].sum().reset_index()
    prod_line_by_month['Month_Year'] = pd.to_datetime(prod_line_by_month['Month_Year'], format='mixed')
    prod_line_by_month = prod_line_by_month.sort_values('Month_Year', ascending=False)
    prod_line_by_month_count = ME1['Month_Year'].value_counts().reset_index()
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
    prod_line_by_year_count['Year'] = pd.Categorical(prod_line_by_year_count['Year'],
                                                     pd.Series([2023,2024]))
    tab31, tab32, tab33 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες"])
    with tab31:
        fig_line_polcou = px.bar(prod_line_by_year_count,
                                 x="Year", y="count",
                                 title='Σύνολο συμβολαίων ανά έτος',
                                 color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                 labels={'count': 'Σύνολο συμβολαίων', 'Year': 'Έτος'}, width=500, text_auto=True)
        fig_line_polcou.update_traces(textfont_size=17, textangle=0,
                                      textposition="outside", cliponaxis=False)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_line_polcou)

        fig_line_polcou = px.line(prod_line_by_month_count,
                                  x="Month_Year", y="count",
                                  title='Σύνολο συμβολαίων ανά μήνα από την έναρξη συνεργασίας',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'count': 'Σύνολο συμβολαίων', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)

        fig_line_polcou = px.line(prod_line_by_month_mean_count.sort_values('Month'),
                                  x="Month", y="count",
                                  title='Σύνολο συμβολαίων ανά μήνα',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'count': 'Σύνολο συμβολαίων', 'Month': 'Μήνας'}, markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)

    with tab32:
        fig_line_polcou = px.bar(prod_line_by_year,
                                 x="Year", y="Net",
                                 title='Καθαρά ασφάλιστρα ανά έτος',
                                 color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                 labels={'Net': 'Καθαρά €', 'Year': 'Έτος'}, width=500, text='Net')
        fig_line_polcou.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                      textposition="outside", cliponaxis=False)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_line_polcou)
        fig_line_net = px.line(prod_line_by_month,
                               x="Month_Year", y="Net",
                               title='Κάθαρα Ασφάλιστρα ανά μήνα από την έναρξη συνεργασίας',
                               color_discrete_sequence=px.colors.sequential.Aggrnyl,
                               labels={'Net': 'Καθαρά €', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
        fig_line_net.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_net)
        fig_line_polcou = px.line(prod_line_by_month_mean.sort_values('Month'),
                                  x="Month", y="Net",
                                  title='Μέσος όρος καθαρών ασφαλίστρων ανά μήνα',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'Net': 'Καθαρά €', 'Month': 'Μήνας'}, markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)
    with tab33:
        fig_line_polcou = px.bar(prod_line_by_year,
                                 x="Year", y="Commissions",
                                 title='Προμήθειες ανά έτος',
                                 color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                 labels={'Commissions': 'Προμήθειες €', 'Year': 'Έτος'}, width=500, text='Commissions')
        fig_line_polcou.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0,
                                      textposition="outside", cliponaxis=False)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_line_polcou)
        fig_line_com = px.line(prod_line_by_month,
                               x="Month_Year", y="Commissions",
                               title='Προμήθειες ανά μήνα από την έναρξη συνεργασίας',
                               color_discrete_sequence=px.colors.sequential.Aggrnyl,
                               labels={'Commissions': 'Προμήθειες €', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
        fig_line_com.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_com)

        fig_line_polcou = px.line(prod_line_by_month_mean.sort_values('Month'),
                                  x="Month", y="Commissions",
                                  title='Μέσος όρος προμηθειών ανά μήνα',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'Commissions': 'Προμήθειες €', 'Month': 'Μήνας'}, markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)
with tab4:
    st.write("# Νομός")

    discrict_data = ME1.groupby(['id', 'District'])[['Gross', 'Net', 'Commissions']].sum().reset_index()
    discrict_data_total = ME1.groupby(['District'])[['Gross', 'Net', 'Commissions']].sum().reset_index()
    discrictcount = discrict_data['District'].value_counts().reset_index().sort_values('count')
    fig_barplot_reg = px.bar(discrictcount, x='count', y='District', title='',
                             labels={'count': 'Αρ. Πελατών', 'District': 'Νομός'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text_auto=True, width=1000, height=300)
    fig_barplot_reg.update_traces(textfont_size=14, textangle=0.5, textposition="outside", cliponaxis=False)
    fig_barplot_reg.update_layout(plot_bgcolor='white', font_size=25)
    st.write(fig_barplot_reg)

with tab5:
    select_durations = ME1.loc[
        (ME1['Duration'] == 1) | (ME1['Duration'] == 3) | (ME1['Duration'] == 6) | (ME1['Duration'] == 12)]
    select_duration_total_year = (select_durations[['Duration_gr', 'Month', 'Year']].value_counts().reset_index()).groupby(['Year', "Duration_gr"])[
        'count'].sum().round(1).reset_index()
    fig_dur_bar = px.bar(select_duration_total_year.loc[select_duration_total_year['Duration_gr'] != "Άλλη"],
                         x="Year", y="count",
                         title='Χρονικές διάρκειες συμβολαίων ανά έτος (Συνολικά)', color='Duration_gr',
                         color_discrete_sequence=px.colors.sequential.Aggrnyl,
                         labels={'count': '# Συμβολαίων', 'Year': 'Έτος', "Duration_gr": 'Διάρκεια συμβολαίου'},
                         width=700, text='count', height=800)
    fig_dur_bar.update_traces(textfont_size=17, textangle=0,cliponaxis=False)
    fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
    st.write(fig_dur_bar)

    select_durations = ME1.loc[
        (ME1['Duration'] == 1) | (ME1['Duration'] == 3) | (ME1['Duration'] == 6) | (ME1['Duration'] == 12)]
    select_duration_total = select_durations[['Duration_gr', 'Month']].value_counts().reset_index().sort_values(
        ['Duration_gr', 'Month'])
    fig_dur_bar = px.bar(select_duration_total,
                         x="Month", y="count",
                         title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Συνολικά)', color='Duration_gr',
                         color_discrete_sequence=px.colors.sequential.Aggrnyl,
                         labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου'},
                         width=1000, text='count')
    fig_dur_bar.update_traces(textfont_size=17, textangle=0,  cliponaxis=False)
    fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
    st.write(fig_dur_bar)
    select_duration_mean = \
    (select_durations[['Duration_gr', 'Month', 'Year']].value_counts().reset_index()).groupby(['Month', "Duration_gr"])[
        'count'].mean().round(1).reset_index()
    fig_dur_bar = px.line(select_duration_mean.loc[select_duration_mean['Duration_gr'] != "Άλλη"],
                          x="Month", y="count",
                          title='Χρονικές διάρκειες συμβολαίων ανά μήνα (Μέσος όρος)', color='Duration_gr',
                          color_discrete_sequence=px.colors.sequential.Aggrnyl,
                          labels={'count': '# Συμβολαίων', 'Month': 'Μήνας', "Duration_gr": 'Διάρκεια συμβολαίου'},
                          width=1000, height=1000, markers=True)
    fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
    st.write(fig_dur_bar)
