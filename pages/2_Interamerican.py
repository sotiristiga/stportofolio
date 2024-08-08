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


st.set_page_config(layout='wide', page_title="Παραγώγη ανα εταιρεία")
ANY = pd.read_csv(f"https://raw.githubusercontent.com/sotiristiga/Tiganitas_Sotiris_portofolio/main/ANY.csv")

ANY['Started'] = pd.to_datetime(ANY['Started'], dayfirst=True)
ANY['Expired'] = pd.to_datetime(ANY['Expired'], dayfirst=True)

ANY['Year'] = ANY['Started'].dt.year
ANY['Year'] = pd.Categorical(ANY['Year'], categories=pd.Series([2024]))
month_levels = pd.Series([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

ANY['Month'] = ANY['Started'].dt.month_name()

ANY['Month'] = pd.Categorical(ANY['Month'], categories=month_levels)

ANY['Month_Year'] = ANY["Started"].dt.strftime('%m-%Y')


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


ANY['Duration'] = (
            (ANY['Expired'].dt.year - ANY['Started'].dt.year) * 12 + ANY['Expired'].dt.month - ANY['Started'].dt.month +
            ANY['Expired'].dt.day / 30 - ANY['Started'].dt.day / 30).round(0)

ANY['Duration_gr'] = ANY['Duration'].apply(duration_groups)

duration_levels = pd.Series(["Ετήσιο", "Εξάμηνο", "Τρίμηνο", "Μηνιαίο", "Άλλη"])

ANY['Duration_gr'] = pd.Categorical(ANY['Duration_gr'], categories=duration_levels)

dynamic_filters1 = DynamicFilters(ANY, filters=['Year', 'Month'])

with st.sidebar:
    dynamic_filters1.display_filters()

ANY1 = dynamic_filters1.filter_df()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-users", "Πελάτες", ANY1['id'].nunique()),
                unsafe_allow_html=True)

with kpi2:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-file-contract", "Συμβόλαια", ANY1['N_Policy'].nunique()),
                unsafe_allow_html=True)

with kpi3:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Καθαρά Ασφάλιστρα", ANY1['Net'].sum().round(2)),
        unsafe_allow_html=True)
with kpi4:
    st.markdown(
        lnk + metrics_customize(0, 204, 102, "fas fa-euro-sign", "Προμήθειες", ANY1['Commissions'].sum().round(2)),
        unsafe_allow_html=True)

with kpi5:
    st.markdown(lnk + metrics_customize(0, 204, 102, "fas fa-percent", "Ποσοστό Προμήθειας",
                                        ((ANY1['Commissions'].sum() / ANY1['Net'].sum()).round(3) * 100)),
                unsafe_allow_html=True)


tab1, tab2, tab4 = st.tabs(
    ["Εξέλιξη Παραγωγής", "Κλάδος ασφάλισης", 'Διάρκειες Συμβολαίων'])
with tab1:
    prod_line_by_month = ANY1.groupby('Month_Year')[['Commissions', "Net"]].sum().reset_index()
    prod_line_by_month['Month_Year'] = pd.to_datetime(prod_line_by_month['Month_Year'], format='mixed')
    prod_line_by_month = prod_line_by_month.sort_values('Month_Year', ascending=False)
    prod_line_by_month_count = ANY1['Month_Year'].value_counts().reset_index()
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
    tab11, tab12, tab13 = st.tabs(["Σύνολο Συμβολαίων", "Καθαρά", "Προμήθειες"])
    with tab11:
            fig_line_polcou = px.bar(prod_line_by_year_count,
                                     x="Year", y="count",
                                     title='Σύνολο συμβολαίων ανά έτος',
                                     color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                     labels={'count': 'Σύνολο συμβολαίων', 'Year': 'Έτος'}, width=800, text_auto=True)
            fig_line_polcou.update_traces(textfont_size=17, textangle=0,
                                          textposition="outside", cliponaxis=False)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=15)
            st.write(fig_line_polcou)

            fig_line_polcou = px.line(prod_line_by_month_count,
                                      x="Month_Year", y="count",
                                      title='Σύνολο συμβολαίων ανά μήνα',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'count': 'Σύνολο συμβολαίων', 'Month_Year': 'Μήνας-Έτος'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)

            fig_line_polcou = px.line(prod_line_by_month_mean_count.sort_values('Month'),
                                      x="Month", y="count",
                                      title='Σύνολο συμβολαίων ανά μήνα απο την έναρξη επαγγέλματος',
                                      color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                      labels={'count': 'Σύνολο συμβολαίων', 'Month': 'Μήνας'}, markers=True)
            fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
            st.write(fig_line_polcou)

    with tab12:
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
                               title='Κάθαρα Ασφάλιστρα ανά μήνα ',
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

    with tab13:
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
            fig_line_com = px.line(prod_line_by_month,
                                   x="Month_Year", y="Commissions",
                                   title='Προμήθειες ανά μήνα',
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
with tab2:
    st.write("### Συνολική παραγωγή ανά κλάδο ασφάλισης")
    col1, col2, col3 = st.columns(3)
    with col1:
        categories_countpol = ANY1['Category'].value_counts().reset_index()
        fig_barplot = px.bar(categories_countpol.sort_values("count"), x='count', y='Category', title='',
                             labels={'count': 'Σύνολο Συμβολαίων', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn,
                             text_auto=True, width=1000, height=400)
        fig_barplot.update_traces(textfont_size=20, textangle=0, textposition="inside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)
    with col2:
        categories_net = ANY1.groupby('Category')['Net'].sum().reset_index()
        categories_net_sorted = categories_net.sort_values('Net', ascending=True)
        fig_barplot = px.bar(categories_net_sorted, x='Net', y='Category', title='',
                             labels={'Net': 'Καθαρά €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Net', width=1000, height=400)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.3s} €', textangle=0, textposition="inside",
                                  cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=40)
        st.write(fig_barplot)
    with col3:
        categories_comm = ANY1.groupby('Category')['Commissions'].sum().reset_index()
        categories_comm_sorted = categories_comm.sort_values('Commissions', ascending=True)
        fig_barplot = px.bar(categories_comm_sorted, x='Commissions', y='Category', title='',
                             labels={'Commissions': 'Προμήθειες €', 'Category': 'Κλάδος'},
                             color_discrete_sequence=px.colors.sequential.Blugrn, text='Commissions', width=1000,
                             height=400)
        fig_barplot.update_traces(textfont_size=17, texttemplate='%{text:.2s} €', textangle=0,
                                  textposition="inside", cliponaxis=False)
        fig_barplot.update_layout(plot_bgcolor='white', font_size=15)
        st.write(fig_barplot)


    tabs24, tabs25, tabs26 = st.tabs(['Συμβόλαια', 'Καθαρά Ασφάλιστρα', "Προμήθειες"])
    cat_mean_month = pd.merge(
        ANY1[['Category', 'Month', 'Month_Year']].value_counts().reset_index().groupby(['Month', "Category"])[
            'count'].mean().reset_index().round(1),
        ANY1.groupby(['Category', 'Month', 'Month_Year'])[["Net", "Commissions"]].sum().reset_index().groupby(
            ['Month', "Category"])[["Net", "Commissions"]].mean().reset_index().round(1))
    with tabs24:
        st.write("### Συνολικά συμβόλαια ανά μήνα από κάθε κλάδο ασφάλισης κατά μέσο όρο")
        cat_mean_month_cou = px.bar(cat_mean_month, x='Month', y='count', title='',
                                    labels={'count': 'Συνολικά συμβόλαια', 'Category': 'Κλάδος'}, color='Category',
                                    color_discrete_sequence=px.colors.sequential.Blugrn, text='count', width=1000,
                                    height=700)
        cat_mean_month_cou.update_traces(textfont_size=17, texttemplate='%{text:.2s}', textangle=0,
                                         textposition="inside", cliponaxis=False)
        cat_mean_month_cou.update_layout(plot_bgcolor='white', font_size=15)
        st.write(cat_mean_month_cou)
    with tabs25:
        st.write("### Καθαρά ασφάλιστρα ανά μήνα από κάθε κλάδο ασφάλισης κατά μέσο όρο")
        cat_mean_month_com = px.bar(cat_mean_month, x='Month', y='Commissions', title='',
                                    labels={'Net': 'Καθαρά ασφάλιστρα', 'Category': 'Κλάδος'}, color='Category',
                                    color_discrete_sequence=px.colors.sequential.Blugrn, text='Net', width=1000,
                                    height=700)
        cat_mean_month_com.update_traces(textfont_size=17, texttemplate='%{text:.2s}', textangle=0,
                                         textposition="inside", cliponaxis=False)
        cat_mean_month_com.update_layout(plot_bgcolor='white', font_size=15)
        st.write(cat_mean_month_com)
    with tabs26:
        st.write("### Προμήθειες ανά μήνα από κάθε κλάδο ασφάλισης κατά μέσο όρο")
        cat_mean_month_com = px.bar(cat_mean_month, x='Month', y='Commissions', title='',
                                    labels={'Commissions': 'Προμήθειες', 'Category': 'Κλάδος'}, color='Category',
                                    color_discrete_sequence=px.colors.sequential.Blugrn, text='Commissions', width=1000,
                                    height=700)
        cat_mean_month_com.update_traces(textfont_size=17, texttemplate='%{text:.2s}', textangle=0,
                                         textposition="inside", cliponaxis=False)
        cat_mean_month_com.update_layout(plot_bgcolor='white', font_size=15)
        st.write(cat_mean_month_com)
    cat_dur_mean_month = ANY1[['Category', 'Month', 'Month_Year', "Duration_gr"]].value_counts().reset_index().groupby(
        ['Month', "Category", "Duration_gr"])['count'].mean().reset_index().round(1)
    st.write("### Συνολικά συμβόλαια ανά κλάδο ασφάλισης και οι διάρκειες τους")
    option1 = st.selectbox("Κλάδος Ασφάλισης", pd.unique(cat_dur_mean_month['Category']))
    cat_mean_month_com = px.bar(cat_dur_mean_month[cat_dur_mean_month['Category'] == option1], x='Month', y='count',
                                title='',
                                labels={'count': 'Συνολικά συμβόλαια', 'Category': 'Κλάδος', 'Month': 'Μήνας',
                                        "Duration_gr": 'Διάρκεια Συμβολαίων'}, color='Duration_gr',
                                color_discrete_sequence=px.colors.sequential.Blugrn, text_auto=True, width=1000,
                                height=700)
    cat_mean_month_com.update_traces(textfont_size=17, textangle=0,
                                     textposition="inside", cliponaxis=False)
    cat_mean_month_com.update_layout(plot_bgcolor='white', font_size=15)
    st.write(cat_mean_month_com)

    st.write("### Εξέλιξη παραγώγης ανά έτος σε κάθε κλάδος ασφάλισης")
    tabs21, tabs22, tabs23 = st.columns(3)
    with tabs21:
        cat_sum_year = pd.merge(ANY1.groupby(['Category', 'Year'])[['Commissions', 'Net']].sum().reset_index(),
                                ANY1[['Category', 'Year']].value_counts().reset_index())
        fig_line_polcou = px.line(cat_sum_year,
                                  x="Year", y="count", color='Category',
                                  title='Σύνολο συμβολαίων',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'count': 'Σύνολο συμβολαίων', 'Year': 'Έτος', "Category": "Κλάδος"},
                                  markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)

    with tabs22:
        fig_line_polcou = px.line(cat_sum_year,
                                  x="Year", y="Net", color='Category',
                                  title='Καθαρά ασφάλιστρά',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'Net': 'Καθαρά', 'Year': 'Έτος', "Category": "Κλάδος"}, markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)
    with tabs23:
        fig_line_polcou = px.line(cat_sum_year,
                                  x="Year", y="Commissions", color='Category',
                                  title='Προμήθειες',
                                  color_discrete_sequence=px.colors.sequential.Aggrnyl,
                                  labels={'Commissions': 'Προμήθειες', 'Year': 'Έτος', "Category": "Κλάδος"},
                                  markers=True)
        fig_line_polcou.update_layout(plot_bgcolor='white', font_size=13)
        st.write(fig_line_polcou)
with tab4:
    select_durations = ANY1.loc[
        (ANY1['Duration'] == 1) | (ANY1['Duration'] == 3) | (ANY1['Duration'] == 6) | (ANY1['Duration'] == 12)]
    select_duration_total_year =(select_durations[['Duration_gr', 'Month', 'Year']].value_counts().reset_index()).groupby(['Year', "Duration_gr"])[
        'count'].sum().round(1).reset_index()
    fig_dur_bar = px.bar(select_duration_total_year.loc[select_duration_total_year['Duration_gr'] != "Άλλη"],
                         x="Year", y="count",
                         title='Χρονικές διάρκειες συμβολαίων ανά έτος (Συνολικά)', color='Duration_gr',
                         color_discrete_sequence=px.colors.sequential.Aggrnyl,
                         labels={'count': '# Συμβολαίων', 'Year': 'Έτος', "Duration_gr": 'Διάρκεια συμβολαίου'},
                         width=900, text='count', height=800)
    fig_dur_bar.update_traces(textfont_size=17, textangle=0,  cliponaxis=False)
    fig_dur_bar.update_layout(plot_bgcolor='white', font_size=15)
    st.write(fig_dur_bar)

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


