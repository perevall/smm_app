import streamlit as st
import requests as r
import json
import plotly.graph_objects as go
import plotly_express as px
import plotly as pl
import pandas as pd
import io
from plotly.subplots import make_subplots
import datetime
import matplotlib as plt
import numpy as np
import time

def round_values(value):
    if isinstance(value, (int, np.int64, float, np.float64)):
        return round(value, 2)
    elif isinstance(value, np.ndarray):
        return np.round(value, 2)
    elif isinstance(value, float) and np.isnan(value):
        return np.nan
    elif isinstance(value, float) and np.isinf(value):
        return np.inf
    else:
        return value

def get_time():
    url = 'https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Amsterdam'
    response_time = r.get(url)
    a = response_time.content.decode('utf-8')
    a = a.replace('true', '""')
    a = a.replace('false', '""')
    b = eval(a)
    return(b.get('dateTime'))



@st.cache_data
def campaign_report(start_time, end_time, campaign = 1):
    headers = {
           # OAuth-токен. Использование слова Bearer обязательно
           "Authorization": "Bearer " + token,
           # Логин клиента рекламного агентства
           "Client-Login": clientLogin,
           # Язык ответных сообщений
           "Accept-Language": "en",
           # Режим формирования отчета
           "processingMode": "auto",
           # Формат денежных значений в отчете
            "returnMoneyInMicros": "false",
           # Не выводить в отчете строку с названием отчета и диапазоном дат
           "skipReportHeader": "true",
           # Не выводить в отчете строку с количеством строк статистики
           "skipReportSummary": "true"
           }
    body = {
        "params": {
        "SelectionCriteria": {
            "DateFrom": start_time,
            "DateTo": end_time
        },
        "FieldNames": [
            "CampaignName",
            "AvgCpc",
            "Clicks",
            "ConversionRate",
            "Conversions",
            "Cost",
            "CostPerConversion",
            "Ctr",
            "Date",
            "Impressions",
        ],
        "ReportName": get_time(),
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "DateRangeType": "CUSTOM_DATE", #оставляем так, чтобы иметь возможность настраивать
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
            }
        }
    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)

    while True:
        try:
            response = r.post(ReportsURL, body, headers=headers)
            if response.status_code == 200:
                break
            if response.status_code == 400 or response.status_code == 500:
                st.subheader('Попробуйте повторить запрос позднее или выбрать другие даты')
                exit()
            if response.status_code == 201 or response.status_code == 202:
                retryIn = int(response1.headers.get("retryIn", 60))
                with st.spinner('Отчет формируется, подождите немного'):
                    time.sleep(5 + retryIn)
                continue
            if response.status_code == 502:
                st.subheader('Попробуйте уменьшить диапозон дат')
                exit()

        except:
            if response.status_code in [400, 500, 502]:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
            else:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
    c = response.content.decode("utf8")
    df = pd.read_csv(io.StringIO(c), header = 0, sep = '\t', na_values=['--']).fillna(0)
    return(df, response)

@st.cache_data
def key_report(start_time, end_time):
    # --- Подготовка запроса ---
    # Создание HTTP-заголовков запроса
    headers = {
           # OAuth-токен. Использование слова Bearer обязательно
           "Authorization": "Bearer " + token,
           # Логин клиента рекламного агентства
           "Client-Login": clientLogin,
           # Язык ответных сообщений
           "Accept-Language": "en",
           # Режим формирования отчета
           "processingMode": "auto",
           # Формат денежных значений в отчете
            "returnMoneyInMicros": "false",
           # Не выводить в отчете строку с названием отчета и диапазоном дат
           "skipReportHeader": "true",
           # Не выводить в отчете строку с количеством строк статистики
           "skipReportSummary": "true"
           }

    # Создание тела запроса
    body = {
        "params": {
        "SelectionCriteria": {
            "Filter" : [
                {
                    "Field" : "Clicks",
                    "Operator" : "GREATER_THAN",
                    "Values" : [
                        "0"
                    ]
                },
                {
                    "Field" : "AdNetworkType",
                    "Operator" : "EQUALS",
                    "Values" : [
                        "SEARCH"
                    ]
                }
            ],
            "DateFrom": start_time,
            "DateTo": end_time
        },
        "FieldNames": [
            "CampaignName",
            "Criterion",
            "AvgCpc",
            "Clicks",
            "ConversionRate",
            "Conversions",
            "Cost",
            "CostPerConversion",
            "Ctr",
            #"Date",
            "Impressions"
        ],
        "ReportName": get_time(),
        "ReportType": "CRITERIA_PERFORMANCE_REPORT",
        "DateRangeType": "CUSTOM_DATE", #оставляем так, чтобы иметь возможность настраивать
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
            }
        }

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)

    while True:
        try:
            response1 = r.post(ReportsURL, body, headers=headers)
            if response1.status_code == 200:
                break
            if response1.status_code == 400 or response1.status_code == 500:
                st.subheader('Попробуйте повторить запрос позднее или выбрать другие даты')
                exit()
            if response1.status_code == 201 or response1.status_code == 202:
                retryIn = int(response1.headers.get("retryIn", 60))
                with st.spinner('Отчет формируется, подождите немного'):
                    time.sleep(5 + retryIn)
                continue
            if response1.status_code == 502:
                st.subheader('Попробуйте уменьшить диапозон дат')
                exit()

        except:
            if response1.status_code in [400, 500, 502]:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
            else:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
    c = response1.content.decode("utf8")
    df_key = pd.read_csv(io.StringIO(c), header = 0, sep = '\t', na_values=['--']).fillna(0)
    return(df_key, response1)

@st.cache_data
def ad_report(start_time, end_time):
    # --- Подготовка запроса ---
    # Создание HTTP-заголовков запроса
    headers = {
           # OAuth-токен. Использование слова Bearer обязательно
           "Authorization": "Bearer " + token,
           # Логин клиента рекламного агентства
           "Client-Login": clientLogin,
           # Язык ответных сообщений
           "Accept-Language": "en",
           # Режим формирования отчета
           "processingMode": "auto",
           # Формат денежных значений в отчете
            "returnMoneyInMicros": "false",
           # Не выводить в отчете строку с названием отчета и диапазоном дат
           "skipReportHeader": "true",
           # Не выводить в отчете строку с количеством строк статистики
           "skipReportSummary": "true"
           }

    # Создание тела запроса
    body = {
        "params": {
        "SelectionCriteria": {
            "DateFrom": start_time,
            "DateTo": end_time
        },
        "FieldNames": [
            "CampaignName",
            "AdId",
            #"Criterion",
            "AvgCpc",
            "Clicks",
            "ConversionRate",
            "Conversions",
            "Cost",
            "CostPerConversion",
            "Ctr",
            #"Date",
            "Impressions"
        ],
        "ReportName": get_time(),
        "ReportType": "AD_PERFORMANCE_REPORT",
        "DateRangeType": "CUSTOM_DATE", #оставляем так, чтобы иметь возможность настраивать
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
            }
        }

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)

    while True:
        try:
            response1 = r.post(ReportsURL, body, headers=headers)
            if response1.status_code == 200:
                break
            if response1.status_code == 400 or response1.status_code == 500:
                st.subheader('Попробуйте повторить запрос позднее или выбрать другие даты')
                exit()
            if response1.status_code == 201 or response1.status_code == 202:
                retryIn = int(response1.headers.get("retryIn", 60))
                with st.spinner('Отчет формируется, подождите немного'):
                    time.sleep(5 + retryIn)
                continue
            if response1.status_code == 502:
                st.subheader('Попробуйте уменьшить диапозон дат')
                exit()

        except:
            if response1.status_code in [400, 500, 502]:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
            else:
                st.subheader('В указанный промежуток времени нет данных, выберите другие даты')
                exit()
    c = response1.content.decode("utf8")
    df = pd.read_csv(io.StringIO(c), header = 0, sep = '\t', na_values=['--']).fillna(0)
    return(df, response1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #задаем размеры приложения
    st.set_page_config(page_title="My Streamlit App", layout="wide")
    #стартуем код
    clientLogin = st.text_input(label = 'Введите логин')
    token = st.text_input(label = 'Введите токен', type = "password")



    CampaignsURL = 'https://api.direct.yandex.com/json/v5/campaigns'

    headers = {"Authorization": "Bearer " + token,  # OAuth-токен. Использование слова Bearer обязательно
           "Client-Login": clientLogin,  # Логин клиента рекламного агентства
           "Accept-Language": "ru",  # Язык ответных сообщений
           }

    # Создание тела запроса
    body = {"method": "get",  # Используемый метод.
        "params": {"SelectionCriteria": {},  # Критерий отбора кампаний. Для получения всех кампаний должен быть пустым
                   "FieldNames": ["Name", "StartDate"]  # Имена параметров, которые требуется получить.
                   }}

    # Кодирование тела запроса в JSON
    jsonBody = json.dumps(body, ensure_ascii=False).encode('utf8')
    if len(clientLogin) > 0 and len(token) > 0:
        try:
            response = r.post(CampaignsURL, jsonBody, headers=headers)
            a = response.content.decode('utf8')
            b = eval(a)
            frame_with_campaigns = pd.DataFrame(b.get('result').get('Campaigns'))
        except:
            st.write("Вы ввели неверный логин или токен")
            exit()
    else:
        exit()


    st.write('Какие есть кампании')
    st.write(frame_with_campaigns)

    year = int(frame_with_campaigns.StartDate.max()[0:4])
    month = int(frame_with_campaigns.StartDate.max()[5:7])
    day = int(frame_with_campaigns.StartDate.max()[8:])


    # --- Входные данные ---
    ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'
    # Адрес сервиса Reports для отправки JSON-запросов (регистрозависимый)



    tab_single_campaign, tab_compare_two, tab_multiple_campaign, tab_key_phrase, tab_inner_ad = st.tabs(["Исследование одной кампании", "Сравнение двух кампаний", "Сравнение кампаний", "Ключевые фразы", "Объявления внутри кампании"])
    with tab_single_campaign:

        with st.form("Параметры отчета"):
            campaign = st.selectbox(label = 'Выберите кампанию', options = frame_with_campaigns.Name)
            date_range = st.date_input(label = 'Выберите даты', value = [datetime.date(year, month, day), datetime.date(year, month, day + 1)])
            start_point_single = str(date_range[0])
            end_point_single = str(date_range[1])

            submitted = st.form_submit_button("Сформировать отчет")
            if submitted:
                df_wrk_single, response = campaign_report(start_time=start_point_single, end_time=end_point_single)
            else:
                pass

        if submitted:
            try:
                df_single = df_wrk_single[df_wrk_single['CampaignName'] == campaign]


                col1, col2, col3 = st.columns(3)

                with col1:

                    col_1_1, col_1_2, col_1_3 = st.columns(3)
                    df_wrk_col_1_3 = df_single[df_single['Date'] == end_point_single]

                    with col_1_1:
                        st.metric(label = "Clicks", value =  df_single.Clicks.sum(), delta = int(df_wrk_col_1_3.Clicks.iloc[0]))
                    with col_1_2:
                        df_wrk_col_1_2 = df_single[df_single['Date'] != end_point_single]
                        st.metric(label = "CTR, %", value =  str(round((df_single.Clicks.sum() / df_single.Impressions.sum()) * 100, 2)),
                                delta = round((((df_single.Clicks.sum() / df_single.Impressions.sum()) * 100) - (df_wrk_col_1_2.Clicks.sum() / df_wrk_col_1_2.Impressions.sum()) * 100), 2)
                                )
                    with col_1_3:
                        st.metric(label = "Impressions", value = df_single.Impressions.sum(), delta = int(df_wrk_col_1_3.Impressions.iloc[0]))

                    fig_clicks_single = go.Figure()

                    fig_clicks_single.add_trace(go.Bar(
                        x=df_single.Date,
                        y=df_single.Clicks,
                        #mode='lines',
                        name=campaign
                        ))
                    fig_clicks_single.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                            )
                    fig_clicks_single.update_layout(title='Clicks',
                            xaxis_title='Date',
                            yaxis_title='Clicks'
                                                    )

                    st.plotly_chart(fig_clicks_single, use_container_width=True, theme="streamlit")

                    fig_ctr_single = go.Figure()

                    fig_ctr_single.add_trace(go.Bar(
                    x=df_single.Date,
                    y=df_single.Ctr,
                    #mode='lines',
                    name=campaign
                    ))
                    fig_ctr_single.update_layout(
                    legend = dict(
                        orientation = 'h',
                        y= -0.3
                        )
                    )
                    fig_ctr_single.update_layout(title='CTR, %',
                        xaxis_title='Date',
                        yaxis_title='CTR, %')

                    st.plotly_chart(fig_ctr_single, use_container_width=True, theme="streamlit")


                with col2:

                    col_2_1, col_2_2, col_2_3 = st.columns(3)
                    df_wrk_col_2_ = df_single[df_single['Date'] != end_point_single]
                    #df_wrk_col_1_3 = df_single[df_single['Date'] == end_point_single]
                    with col_2_1:
                        st.metric(label = "Cost, руб.", value = int(df_single.Cost.sum()),
                                  delta = int(df_wrk_col_1_3.Cost.iloc[0]), delta_color="off"
                                  )
                    with col_2_2:
                        st.metric(label = "Avg. CPC, руб.", value = int(df_single.Cost.sum() / df_single.Clicks.sum()),
                                  delta = round((df_single.Cost.sum() / df_single.Clicks.sum()) - (df_wrk_col_2_.Cost.sum() / df_wrk_col_2_.Clicks.sum()), 2),
                                  delta_color="inverse"
                                  )
                    with col_2_3:
                        st.metric(label = "Avg. CPM, руб.", value = int((df_single.Cost.sum() / df_single.Impressions.sum()) * 1000),
                                  delta = round(((df_single.Cost.sum() / df_single.Impressions.sum()) * 1000) - ((df_wrk_col_2_.Cost.sum() / df_wrk_col_2_.Impressions.sum()) * 1000), 2),
                                  delta_color="inverse"
                                  )


                    fig_cost_single = go.Figure()

                    fig_cost_single.add_trace(go.Bar(
                        x=df_single.Date,
                        y=df_single.Cost,
                        #mode='lines',
                        name=campaign
                        ))
                    fig_cost_single.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_cost_single.update_layout(title='Cost, руб.',
                            xaxis_title='Date',
                            yaxis_title='Cost, руб.')

                    st.plotly_chart(fig_cost_single, use_container_width=True, theme="streamlit")

                    fig_costpa_single = go.Figure()

                    fig_costpa_single.add_trace(go.Bar(
                        x=df_single.Date,
                        y=df_single.CostPerConversion,
                        #mode='lines',
                        name=campaign
                        ))
                    fig_costpa_single.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_costpa_single.update_layout(title='Cost Per Action, руб.',
                            xaxis_title='Date',
                            yaxis_title='Cost Per Action, руб.')

                    st.plotly_chart(fig_costpa_single, use_container_width=True, theme="streamlit")

                with col3:
                    col_3_1, col_3_2, col_3_3 = st.columns(3)
                    #df_wrk_col_2_ = df_single[df_single['Date'] != end_point_single]
                    #df_wrk_col_1_3 = df_single[df_single['Date'] == end_point_single]
                    with col_3_1:
                        st.metric(label = "Conversions", value = int(df_single.Conversions.sum()),
                                  delta = int(df_wrk_col_1_3.Conversions.iloc[0])
                                  )
                    with col_3_2:
                        st.metric(label = "Conv. rate, %", value = str(round((df_single.Conversions.sum() / df_single.Clicks.sum()) * 100, 2)),
                                  delta = round(((df_single.Conversions.sum() / df_single.Clicks.sum()) - (df_wrk_col_2_.Conversions.sum() / df_wrk_col_2_.Clicks.sum())) * 100, 2)
                                  )
                    with col_3_3:
                        st.metric(label = "Avg. CPA, руб.", value = int(df_single.Cost.sum() / df_single.Conversions.sum()),
                                  delta = round((df_single.Cost.sum() / df_single.Conversions.sum()) - (df_wrk_col_2_.Cost.sum() / df_wrk_col_2_.Conversions.sum()), 2),
                                  delta_color="inverse"
                                  )

                    fig_conv_single = go.Figure()

                    fig_conv_single.add_trace(go.Bar(
                        x=df_single.Date,
                        y=df_single.Conversions,
                        #mode='lines',
                        name=campaign
                        ))
                    fig_conv_single.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_conv_single.update_layout(title='Conversions',
                            xaxis_title='Date',
                            yaxis_title='Conversions')

                    st.plotly_chart(fig_conv_single, use_container_width=True, theme="streamlit")

                    fig_convr_single = go.Figure()

                    fig_convr_single.add_trace(go.Bar(
                        x=df_single.Date,
                        y=df_single.ConversionRate,
                        #mode='lines',
                        name=campaign
                        ))
                    fig_convr_single.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_convr_single.update_layout(title='Conversion Rate, %',
                            xaxis_title='Date',
                            yaxis_title='Conversion Rate, %')

                    st.plotly_chart(fig_convr_single, use_container_width=True, theme="streamlit")

                st.dataframe(df_single.set_index('Date').rename(columns={"Cost": "Cost, руб.",
                                                        "CostPerClick": "CostPerClick, руб.",
                                                        "CostPerConversion" : "CostPerAction, руб.",
                                                        "ConversionRate" : "ConversionRate, %",
                                                        "Ctr" : "Ctr, %"
                                                        }), use_container_width = True)
            except:
                if response.status_code in [400, 500, 502]:
                    pass
                else:
                    st.subheader("Выберите другую даты или кампанию")
                    pass
        else:
            pass

    with tab_compare_two:

        with st.form("Параметры отчета \t"):
            campaign_one = st.selectbox(label = 'Выберите первую кампанию', options = frame_with_campaigns.Name)
            campaign_two = st.selectbox(label = 'Выберите вторую кампанию', options = frame_with_campaigns.Name)
            date_range_compare = st.date_input(label = 'Выберите даты \t \t', value = [datetime.date(year, month, day), datetime.date(year, month, day + 1)])
            start_point_compare = str(date_range_compare[0])
            end_point_compare = str(date_range_compare[1])

            submitted_two = st.form_submit_button("Сформировать отчет \t")
            if submitted_two:
                df_compare, response = campaign_report(start_time=start_point_compare, end_time=end_point_compare)
            else:
                #df_compare, response = campaign_report(start_time = start_point_compare, end_time = end_point_compare)
                pass
        if submitted_two:
            try:
                df_compare_one = df_compare.loc[df_compare['CampaignName'] == campaign_one]
                df_compare_two = df_compare.loc[df_compare['CampaignName'] == campaign_two]

                col_compare_name, col_compare_clicks, col_compare_ctr, col_compare_impressions, col_compare_cost, col_compare_cpc, col_compare_cpm, col_compare_conversons, col_compare_convr, col_compare_cpa = st.columns(10)

                with col_compare_name:
                    st.write(campaign_one)
                    st.write(campaign_two)

                with col_compare_clicks:
                    df_wrk_col_compare_clicks_1 = df_compare_one[df_compare_one['Date'] == end_point_compare]
                    df_wrk_col_compare_clicks_2 = df_compare_two[df_compare_two['Date'] == end_point_compare]
                    st.metric(label = "Clicks",
                              value =  df_compare_one.Clicks.sum(),
                              delta = int(df_wrk_col_compare_clicks_1.Clicks.iloc[0]))
                    st.metric(label = "Clicks",
                              value =  df_compare_two.Clicks.sum(),
                              delta = int(df_wrk_col_compare_clicks_2.Clicks.iloc[0]))

                with col_compare_ctr:
                    df_wrk_compare_ctr_1 = df_compare_one[df_compare_one['Date'] != end_point_single]
                    df_wrk_compare_ctr_2 = df_compare_two[df_compare_two['Date'] != end_point_single]
                    st.metric(label = "CTR, %", value =  str(round((df_compare_one.Clicks.sum() / df_compare_one.Impressions.sum()) * 100, 2)),
                                delta = round((((df_compare_one.Clicks.sum() / df_compare_one.Impressions.sum()) * 100) - (df_wrk_compare_ctr_1.Clicks.sum() / df_wrk_compare_ctr_1.Impressions.sum()) * 100), 2)
                                )
                    st.metric(label = "CTR, %", value =  str(round((df_compare_two.Clicks.sum() / df_compare_two.Impressions.sum()) * 100, 2)),
                                delta = round((((df_compare_two.Clicks.sum() / df_compare_two.Impressions.sum()) * 100) - (df_wrk_compare_ctr_2.Clicks.sum() / df_wrk_compare_ctr_2.Impressions.sum()) * 100), 2)
                                )

                with col_compare_impressions:
                    st.metric(label = "Impressions", value = df_compare_one.Impressions.sum(), delta = int(df_wrk_col_compare_clicks_1.Impressions.iloc[0]))
                    st.metric(label = "Impressions", value = df_compare_two.Impressions.sum(), delta = int(df_wrk_col_compare_clicks_2.Impressions.iloc[0]))

                with col_compare_cost:
                    st.metric(label = "Cost, руб.", value = int(df_compare_one.Cost.sum()),
                                  delta = int(df_wrk_col_compare_clicks_1.Cost.iloc[0]), delta_color="off"
                                  )
                    st.metric(label = "Cost, руб.", value = int(df_compare_two.Cost.sum()),
                                  delta = int(df_wrk_col_compare_clicks_2.Cost.iloc[0]), delta_color="off"
                                  )

                with col_compare_cpc:
                    st.metric(label = "Avg. CPC, руб.", value = int(df_compare_one.Cost.sum() / df_compare_one.Clicks.sum()),
                                  delta = round((df_compare_one.Cost.sum() / df_compare_one.Clicks.sum()) - (df_wrk_compare_ctr_1.Cost.sum() / df_wrk_compare_ctr_1.Clicks.sum()), 2),
                                  delta_color="inverse"
                                  )
                    st.metric(label = "Avg. CPC, руб.", value = int(df_compare_two.Cost.sum() / df_compare_two.Clicks.sum()),
                                  delta = round((df_compare_two.Cost.sum() / df_compare_two.Clicks.sum()) - (df_wrk_compare_ctr_2.Cost.sum() / df_wrk_compare_ctr_2.Clicks.sum()), 2),
                                  delta_color="inverse"
                                  )
                with col_compare_cpm:
                    st.metric(label = "Avg. CPM, руб.", value = int((df_compare_one.Cost.sum() / df_compare_one.Impressions.sum()) * 1000),
                                  delta = round(((df_compare_one.Cost.sum() / df_compare_one.Impressions.sum()) * 1000) - ((df_wrk_compare_ctr_1.Cost.sum() / df_wrk_compare_ctr_1.Impressions.sum()) * 1000), 2),
                                  delta_color="inverse"
                                  )
                    st.metric(label = "Avg. CPM, руб.", value = int((df_compare_two.Cost.sum() / df_compare_two.Impressions.sum()) * 1000),
                                  delta = round(((df_compare_two.Cost.sum() / df_compare_two.Impressions.sum()) * 1000) - ((df_wrk_compare_ctr_2.Cost.sum() / df_wrk_compare_ctr_2.Impressions.sum()) * 1000), 2),
                                  delta_color="inverse"
                                  )

                with col_compare_conversons:
                    st.metric(label = "Conversions", value = int(df_compare_one.Conversions.sum()),
                                  delta = int(df_wrk_col_compare_clicks_1.Conversions.iloc[0])
                                  )
                    st.metric(label = "Conversions", value = int(df_compare_two.Conversions.sum()),
                                  delta = int(df_wrk_col_compare_clicks_2.Conversions.iloc[0])
                                  )

                with col_compare_convr:
                    st.metric(label = "Conv. rate, %", value = str(round((df_compare_one.Conversions.sum() / df_compare_one.Clicks.sum()) * 100, 2)),
                                  delta = round(((df_compare_one.Conversions.sum() / df_compare_one.Clicks.sum()) - (df_wrk_compare_ctr_1.Conversions.sum() / df_wrk_compare_ctr_1.Clicks.sum())) * 100, 2)
                                  )
                    st.metric(label = "Conv. rate, %", value = str(round((df_compare_two.Conversions.sum() / df_compare_two.Clicks.sum()) * 100, 2)),
                                  delta = round(((df_compare_two.Conversions.sum() / df_compare_two.Clicks.sum()) - (df_wrk_compare_ctr_2.Conversions.sum() / df_wrk_compare_ctr_2.Clicks.sum())) * 100, 2)
                                  )

                with col_compare_cpa:
                    st.metric(label = "Avg. CPA, руб.", value = int(df_compare_one.Cost.sum() / df_compare_one.Conversions.sum()),
                                  delta = round((df_compare_one.Cost.sum() / df_compare_one.Conversions.sum()) - (df_wrk_compare_ctr_1.Cost.sum() / df_wrk_compare_ctr_1.Conversions.sum()), 2),
                                  delta_color="inverse"
                                  )
                    st.metric(label = "Avg. CPA, руб.", value = int(df_compare_two.Cost.sum() / df_compare_two.Conversions.sum()),
                                  delta = round((df_compare_two.Cost.sum() / df_compare_two.Conversions.sum()) - (df_wrk_compare_ctr_2.Cost.sum() / df_wrk_compare_ctr_2.Conversions.sum()), 2),
                                  delta_color="inverse"
                                  )








                col_compare_1, col_compare_2, col_compare_3 = st.columns(3)

                with col_compare_1:

                    fig_conv_compare = go.Figure()

                    fig_conv_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.Conversions,
                        #mode='lines',
                        name=campaign_one
                        ))
                    fig_conv_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.Conversions,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_conv_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_conv_compare.update_layout(title='Conversions',
                            xaxis_title='Date',
                            yaxis_title='Conversions')

                    st.plotly_chart(fig_conv_compare, use_container_width=True, theme="streamlit")

                    fig_convrate_compare = go.Figure()

                    fig_convrate_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.ConversionRate,
                        #mode='lines',
                        name=campaign_one
                        ))
                    fig_convrate_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.ConversionRate,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_convrate_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_convrate_compare.update_layout(title='Conversion Rate, %',
                            xaxis_title='Date',
                            yaxis_title='Conversion Rate, %')

                    st.plotly_chart(fig_convrate_compare, use_container_width=True, theme="streamlit")

                with col_compare_2:

                    fig_ctr_compare = go.Figure()

                    fig_ctr_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.Ctr,
                        #mode='lines',
                        name=campaign_one,
                        line = dict(color='blue')
                        ))
                    fig_ctr_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.Ctr,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_ctr_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_ctr_compare.update_layout(title='Ctr per day, %',
                            xaxis_title='Date',
                            yaxis_title='Ctr, %')

                    st.plotly_chart(fig_ctr_compare, use_container_width=True, theme="streamlit")

                    fig_clicks_compare = go.Figure()

                    fig_clicks_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.Clicks,
                        #mode='lines',
                        name=campaign_one
                        ))
                    fig_clicks_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.Clicks,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_clicks_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_clicks_compare.update_layout(title='Clicks per day',
                            xaxis_title='Date',
                            yaxis_title='Clicks')

                    st.plotly_chart(fig_clicks_compare, use_container_width=True, theme="streamlit")

                with col_compare_3:

                    fig_costperconv_compare = go.Figure()
                    fig_costperconv_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.CostPerConversion,
                        #mode='lines',
                        name=campaign_one
                        ))
                    fig_costperconv_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.CostPerConversion,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_costperconv_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_costperconv_compare.update_layout(title='Cost per action, руб.',
                            xaxis_title='Date',
                            yaxis_title='Cost per action, руб.')

                    st.plotly_chart(fig_costperconv_compare, use_container_width=True, theme="streamlit")

                    fig_costperday_compare = go.Figure()
                    fig_costperday_compare.add_trace(go.Scatter(
                        x=df_compare_one.Date,
                        y=df_compare_one.Cost,
                        #mode='lines',
                        name=campaign_one
                        ))
                    fig_costperday_compare.add_trace(go.Scatter(
                        x=df_compare_two.Date,
                        y=df_compare_two.Cost,
                        #mode='lines',
                        name=campaign_two,
                        line = dict(color='red')
                        ))
                    fig_costperday_compare.update_layout(
                        legend = dict(
                            orientation = 'h',
                            y= -0.3
                            )
                        )
                    fig_costperday_compare.update_layout(title='Cost per day, руб.',
                            xaxis_title='Date',
                            yaxis_title='Cost per day, руб.')

                    st.plotly_chart(fig_costperday_compare, use_container_width=True, theme="streamlit")
            except:
                if response.status_code in [400, 500, 502]:
                    pass
                else:
                    st.subheader("Выберите другую даты или кампанию")
                    pass
        else:
            pass



    with tab_multiple_campaign:

        with st.form("Параметры отчета \t\t"):
            date_range_mult = st.date_input(label = 'Выберите даты \t', value = [datetime.date(year, month, day), datetime.date(year, month, day + 1)])
            start_point_mult = str(date_range_mult[0])
            end_point_mult = str(date_range_mult[1])
            xx = 0

            df1, response= campaign_report(start_time = start_point_mult, end_time = end_point_mult)
            drop_campaign_list = st.multiselect(
                label = 'Выберите, какие кампании исключить из анализа',
                options = df1['CampaignName'].unique())

            submit_mult = st.form_submit_button("Сформировать отчет \t\t\t")
            if submit_mult:
                if xx == 0:
                    df_result = df1.copy()
                    for i in drop_campaign_list:
                        df_result = df_result.loc[df_result['CampaignName'] != i]
                    df_mean = df_result.copy()
                    df_mean = df_mean.drop(['CampaignName'], axis = 1)
                    df_mean = df_mean.groupby(['Date']).mean()
                    df_mean = df_mean.reset_index()



                    df_sum = df_result.groupby(['CampaignName']).sum()
                    df_multiple_ctr_wrk = df_sum[['Conversions', 'Cost', 'Clicks', 'Impressions']]
                    df_multiple_ctr_wrk['CostPerClick'] = df_multiple_ctr_wrk['Cost'] / df_multiple_ctr_wrk['Clicks']
                    df_multiple_ctr_wrk['CostPerAction'] = (df_multiple_ctr_wrk['Cost'] / df_multiple_ctr_wrk['Conversions'])
                    df_multiple_ctr_wrk['ConversionRate'] = (df_multiple_ctr_wrk['Conversions'] / df_multiple_ctr_wrk['Clicks']) * 100
                    df_multiple_ctr_wrk['Ctr'] = df_multiple_ctr_wrk['Clicks'] / df_multiple_ctr_wrk['Impressions'] * 100

                    df_multiple_ctr_wrk = df_multiple_ctr_wrk.reset_index()



                    ### боремся с inf в конверсиях
                    for i in range(df_multiple_ctr_wrk.index.min(), df_multiple_ctr_wrk.index.max() + 1):
                        if df_multiple_ctr_wrk.CostPerAction[i] == np.inf or df_multiple_ctr_wrk.CostPerAction[i] == np.nan:
                            df_multiple_ctr_wrk.CostPerAction[i] = None
                        if df_multiple_ctr_wrk.ConversionRate[i] == np.inf or df_multiple_ctr_wrk.ConversionRate[i] == np.nan:
                            df_multiple_ctr_wrk.ConversionRate[i] = None
                        if df_multiple_ctr_wrk.Ctr[i] == np.inf or df_multiple_ctr_wrk.Ctr[i] == np.nan:
                            df_multiple_ctr_wrk.Ctr[i] = None
                        if df_multiple_ctr_wrk.CostPerClick[i] == np.inf or df_multiple_ctr_wrk.CostPerClick[i] == np.nan:
                            df_multiple_ctr_wrk.CostPerClick[i] = None

                    df_multiple_ctr_wrk_2 = df_multiple_ctr_wrk.copy()
                    df_multiple_ctr_wrk.loc[len(df_multiple_ctr_wrk.index)] = df_multiple_ctr_wrk.median(axis=0, skipna=True, numeric_only=True)
                    a = df_multiple_ctr_wrk.index.max()
                    df_multiple_ctr_wrk.iat[a, 0] = 'Median'
                    df_multiple_ctr_wrk.loc[len(df_multiple_ctr_wrk.index)] = df_multiple_ctr_wrk_2.mean(axis=0, skipna=True, numeric_only=True)
                    b = df_multiple_ctr_wrk.index.max()
                    df_multiple_ctr_wrk.iat[b, 0] = 'Mean'

                    df_two_report = df_multiple_ctr_wrk.copy()
                    df_two_report = df_two_report.set_index('CampaignName')

                    df_multiple_ctr_wrk = df_multiple_ctr_wrk.applymap(round_values)
                    df_to_show = df_multiple_ctr_wrk.copy()

                    df_to_show = df_to_show.style.format(precision=2).background_gradient(cmap = "RdBu",
                                                                                       subset=["ConversionRate"],
                                                                                       vmin = df_to_show.ConversionRate.min(),
                                                                                       low = 0
                                                                                       ).background_gradient(cmap = "RdBu",
                                                                                       subset=["Ctr"],
                                                                                       vmin = df_to_show.Ctr.min(),
                                                                                       low = 0
                                                                                       ).background_gradient(cmap = "seismic",
                                                                                       subset=["CostPerClick"],
                                                                                       vmin = df_to_show.CostPerClick.min(),
                                                                                       low = 0
                                                                                       ).background_gradient(cmap = "seismic",
                                                                                       subset=["CostPerAction"],
                                                                                       vmin = df_to_show.CostPerAction.min(),
                                                                                       low = 0
                                                                                       )



                    st.dataframe(df_to_show, width= 2000)

                    st.subheader('Посчитать ДРР')
                    revenue = st.number_input("Введите ваш доход от рекламы")
                    if revenue > 0:
                        st.write("ДРР = ", str(round(((df_multiple_ctr_wrk_2.Cost.sum() * 100) / revenue), 2)) + "%")
                    else:
                        pass




                    df_for_compare = df_multiple_ctr_wrk_2.copy().set_index('CampaignName')

                    tab_multiple_convr, tab_multiple_coversions, tab_multiple_clicks, tab_multiple_impressions, tab_multiple_cost,\
                            tab_multiple_cost_per_conv, tab_multiple_ctr = st.tabs(["Коэф. конверсии",
                                                                        "Конверсии",
                                                                        "Клики",
                                                                        "Показы",
                                                                        "Затраты",
                                                                       "Цена конверсии",
                                                                        "CTR"])

                    with tab_multiple_convr:
                                fig_multiple_convr = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_convr.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.ConversionRate,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_convr.add_trace(go.Scatter(
                                x=df_mean.Date,
                                y=df_mean.ConversionRate,
                                name = 'среднее',
                                line = dict(color='firebrick', width=4, dash='dot'
                                )))
                                fig_multiple_convr.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_convr.update_layout(title='ConversionRate per day, %',
                                        xaxis_title='Date',
                                        yaxis_title='ConversionRate, %')

                                st.plotly_chart(fig_multiple_convr, use_container_width=True, theme="streamlit")

                    with tab_multiple_coversions:
                                fig_multiple_conversions = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_conversions.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.Conversions,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_conversions.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.Conversions,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                )))
                                fig_multiple_conversions.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_conversions.update_layout(title='Conversions per day',
                                        xaxis_title='Date',
                                        yaxis_title='Conversions')

                                st.plotly_chart(fig_multiple_conversions, use_container_width=True, theme="streamlit")

                    with tab_multiple_clicks:
                                fig_multiple_clicks = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_clicks.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.Clicks,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_clicks.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.Clicks,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                    )))
                                fig_multiple_clicks.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_clicks.update_layout(title='Clicks per day',
                                        xaxis_title='Date',
                                        yaxis_title='Clicks')

                                st.plotly_chart(fig_multiple_clicks, use_container_width=True, theme="streamlit")

                    with tab_multiple_impressions:
                                fig_multiple_impressions = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_impressions.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.Impressions,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_impressions.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.Impressions,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                    )))
                                fig_multiple_impressions.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_impressions.update_layout(title='Impressions per day',
                                        xaxis_title='Date',
                                        yaxis_title='Impressions')

                                st.plotly_chart(fig_multiple_impressions, use_container_width=True, theme="streamlit")

                    with tab_multiple_cost:
                                fig_multiple_cost = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_cost.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.Cost,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_cost.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.Cost,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                    )))
                                fig_multiple_cost.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_cost.update_layout(title='Costs per day, руб.',
                                        xaxis_title='Date',
                                        yaxis_title='Costs, руб.')

                                st.plotly_chart(fig_multiple_cost, use_container_width=True, theme="streamlit")

                    with tab_multiple_cost_per_conv:
                                fig_multiple_cost_per_conv = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_cost_per_conv.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.CostPerConversion,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_cost_per_conv.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.CostPerConversion,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                    )))
                                fig_multiple_cost_per_conv.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_cost_per_conv.update_layout(title='Costs per conversion, руб.',
                                        xaxis_title='Date',
                                        yaxis_title='Cost per conversion, руб.')

                                st.plotly_chart(fig_multiple_cost, use_container_width=True, theme="streamlit")


                    with tab_multiple_ctr:
                                fig_multiple_ctr = go.Figure()
                                for i in df_result['CampaignName'].unique():
                                    df_wrk = df_result[df_result['CampaignName'] == i]
                                    fig_multiple_ctr.add_trace(go.Scatter(
                                        x=df_wrk.Date,
                                        y=df_wrk.Ctr,
                                        #mode='lines',
                                        name=i
                                        ))
                                fig_multiple_ctr.add_trace(go.Scatter(
                                    x=df_mean.Date,
                                    y=df_mean.Ctr,
                                    name = 'среднее',
                                    line = dict(color='firebrick', width=4, dash='dot'
                                    )))
                                fig_multiple_ctr.update_layout(
                                    legend = dict(
                                        orientation = 'h',
                                        y= -0.3
                                        ),
                                    height = 600
                                    )

                                fig_multiple_ctr.update_layout(title='CTR, %',
                                        xaxis_title='Date',
                                        yaxis_title='CTR, %')

                                st.plotly_chart(fig_multiple_ctr, use_container_width=True, theme="streamlit")
                    ##рекомендации по конверсиям
                    st.divider()
                    st.subheader("У данных кампаний за выбранный период CR выше медианы")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["ConversionRate"] > df_two_report.at['Median', 'ConversionRate'] )& (df_multiple_ctr_wrk.CampaignName != 'Mean')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))

                    st.divider()
                    st.subheader("У данных кампаний за выбранный период CR ниже медианы, но не в 2 раза. Рассмотрите данные РК подробнее")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["ConversionRate"] < df_two_report.at['Median', 'ConversionRate']) & (df_multiple_ctr_wrk["ConversionRate"] > df_two_report.at['Mean', 'ConversionRate']/2) & (df_multiple_ctr_wrk.CampaignName != 'Median') & (df_multiple_ctr_wrk.CampaignName != 'Mean')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))

                    st.divider()
                    st.subheader("У данных кампаний за выбранный период CR ниже медианы больше, чем в 2 раза. Рассмотрите данные РК подробнее ")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["ConversionRate"] < df_two_report.at['Median', 'ConversionRate']/2) & (df_multiple_ctr_wrk.CampaignName != 'Mean') & (df_multiple_ctr_wrk.CampaignName != 'Median')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))

                    st.divider()
                    st.subheader("У данных РК нет конверсий")
                    st.dataframe(df_multiple_ctr_wrk[df_multiple_ctr_wrk["ConversionRate"] == 0].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))


                    ##рекомендации по цене цели
                    st.divider()
                    st.subheader("У данных кампаний за выбранный период цена цели (СPA) ниже медианы (чем ниже цена цели, тем лучше)")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["CostPerAction"] < df_two_report.at['Median', 'CostPerAction']) & (df_multiple_ctr_wrk.CampaignName != 'Median') & (df_multiple_ctr_wrk.CampaignName != 'Mean')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))

                    st.divider()
                    st.subheader("У данных кампаний за выбранный период времени цена цели выше медианой цены цели, но не в 2 раза. Рассмотрите РК подробнее")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["CostPerAction"] > df_two_report.at['Median', 'CostPerAction']) & (df_multiple_ctr_wrk.CampaignName != 'Median') & (df_multiple_ctr_wrk["CostPerAction"] < df_two_report.at['Mean', 'CostPerAction']*2) & (df_multiple_ctr_wrk.CampaignName != 'Mean')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))

                    st.divider()
                    st.subheader("У данных кампаний за выбранный период времени цена цели выше медианой цены цели в 2 раза. Рассмотрите РК подробнее")
                    st.dataframe(df_multiple_ctr_wrk[(df_multiple_ctr_wrk["CostPerAction"] > df_two_report.at['Median', 'CostPerAction']*2) & (df_multiple_ctr_wrk.CampaignName != 'Median') & (df_multiple_ctr_wrk.CampaignName != 'Mean')].rename(columns={"Cost": "Cost, руб.",
                                                                    "CostPerClick": "CostPerClick, руб.",
                                                                    "CostPerAction" : "CostPerAction, руб.",
                                                                    "ConversionRate" : "ConversionRate, %",
                                                                    "Ctr" : "Ctr, %"
                                                                    }))
            else:
                pass





    with tab_key_phrase:

        with st.form('Параметры отчета \t\t\t\t'):
            date_range_key = st.date_input(label = 'Выберите даты \t\t\t', value = [datetime.date(year, month, day), datetime.date(year, month, day + 1)])
            start_point_key = str(date_range_key[0])
            end_point_key = str(date_range_key[1])

            submit_key = st.form_submit_button('Сформировать отчет \t\t\t\t')

            if submit_key:
                df_key, response = key_report(start_time = start_point_key, end_time = end_point_key)
            else:
                pass
        try:

            df_key_wrk = df_key.groupby(by = ['Criterion']).sum()
            df_key_wrk = df_key_wrk.reset_index()

            df_key_wrk.loc[len(df_key_wrk.index)] = df_key_wrk.median(axis=0, skipna=True, numeric_only=True)
            a = df_key_wrk.index.max()
            df_key_wrk.iat[a, 0] = 'Median'
            df_key_wrk.loc[len(df_key_wrk.index)] = df_key_wrk.mean(axis=0, skipna=True, numeric_only=True)
            b = df_key_wrk.index.max()
            df_key_wrk.iat[b, 0] = 'Mean'

            ## Пошли отчеты
            df_key_dash_wrk = df_key_wrk.copy()
            df_key_dash_wrk = df_key_dash_wrk.set_index("Criterion")
            st.subheader("Ключевые фразы за выбранный период, где кликов > 0")
            st.dataframe(df_key_wrk.rename(columns={"Cost": "Cost, руб.",
                                                    "CostPerClick": "CostPerClick, руб.",
                                                    "CostPerConversion" : "CostPerAction, руб.",
                                                    "ConversionRate" : "ConversionRate, %",
                                                    "Ctr" : "Ctr, %"
                                                    }), width= 2000)

            st.subheader("Ключевые слова за выбранный период, у которых стоимость конверсии выше медианого уровня на 50%")
            st.dataframe(df_key_wrk[df_key_wrk["CostPerConversion"] > df_key_dash_wrk.at['Median', 'CostPerConversion']*1.5].rename(columns={"Cost": "Cost, руб.",
                                                    "CostPerClick": "CostPerClick, руб.",
                                                    "CostPerConversion" : "CostPerAction, руб.",
                                                    "ConversionRate" : "ConversionRate, %",
                                                    "Ctr" : "Ctr, %"
                                                    }))

            st.subheader("Ключевые слова, по которым расходы составили свыше 150% медианой цены конверсии и которые до сих пор не принесли конверсии")
            st.dataframe(df_key_wrk[(df_key_wrk["Cost"] > df_key_dash_wrk.at['Median', 'CostPerConversion']*1.5) & df_key_wrk["Conversions"] == 0].rename(columns={"Cost": "Cost, руб.",
                                                    "CostPerClick": "CostPerClick, руб.",
                                                    "CostPerConversion" : "CostPerAction, руб.",
                                                    "ConversionRate" : "ConversionRate, %",
                                                    "Ctr" : "Ctr, %"
                                                    }))
        except:
            if response.status_code in [400, 500, 502]:
                pass
            else:
                st.subheader("Выберите другую даты или кампанию")
                pass


    with tab_inner_ad:
        with st.form('Параметры отчета \t\t\t\t\t'):
            date_range_ad = st.date_input(label = 'Выберите даты \t\t\t\t', value = [datetime.date(year, month, day + 1), datetime.date(year, month, day + 1)])
            start_point_ad = str(date_range_ad[0])
            end_point_ad = str(date_range_ad[1])

            submit_ad = st.form_submit_button('Сформировать отчет \t\t\t\t\t')

            if submit_key:
                df_ad, response = ad_report(start_time = start_point_ad, end_time = end_point_ad)
            else:
                pass
        try:

            st.dataframe(df_ad.rename(columns={"Cost": "Cost, руб.",
                                                    "CostPerClick": "CostPerClick, руб.",
                                                    "CostPerConversion" : "CostPerAction, руб.",
                                                    "ConversionRate" : "ConversionRate, %",
                                                    "Ctr" : "Ctr, %"
                                                    }))

            campaign_ad = st.selectbox(label = 'Выберите кампанию \t\t\t\t\t\t', options = df_ad.CampaignName.unique())

            df_ad_wrk = df_ad[df_ad["CampaignName"] == campaign_ad]
            df_ad_wrk_2 = df_ad_wrk.sort_values(by = ['Ctr'], ascending=False).reset_index()
            df_ad_wrk_2 = df_ad_wrk_2.drop(['index'], axis=1)

            st.subheader("Обявление " + str(df_ad_wrk_2.AdId[0]) + ' имеет самый высокий Ctr')
            st.dataframe(df_ad_wrk_2.rename(columns={"Cost": "Cost, руб.",
                                                    "CostPerClick": "CostPerClick, руб.",
                                                    "CostPerConversion" : "CostPerAction, руб.",
                                                    "ConversionRate" : "ConversionRate, %",
                                                    "Ctr" : "Ctr, %"
                                                    }))
        except:
            if response.status_code in [400, 500, 502]:
                pass
            else:
                st.subheader("Выберите другую даты или кампанию")
                pass











