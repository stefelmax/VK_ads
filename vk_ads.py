import vk_api
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import numpy as np

token = 'Сюда нужно вставить токен'

session = vk_api.VkApi(token=token)
vk = session.get_api()

# Получаем список кампаний по id рекламного аккаунта
def get_campaigns(id):
    camp = vk.ads.getCampaigns(account_id=id)
    return camp

def get_ads(id, campaigns):
    lst = []
    arr = []
    campaign_list = json.dumps([i['id'] for i in campaigns])
    ads = vk.ads.getAds(account_id=id, campaign_ids=campaign_list, include_deleted=0)

    for ad in ads:
        # lst.append([ad['id'], ad['campaign_id'], ad['day_limit']])
        arr.append({'id': ad['id'], 'campaign_id': ad['campaign_id'], 'day_limit': ad['day_limit']})

    # df = pd.DataFrame(lst, columns=['id', 'campaign_id', 'day_limit'])
    return arr


# Для каждой рекламной кампании выгружаем статистику
def get_stat(id, campaign, date_start, date_end, ids_type) -> list:
    new_data = []

    for c in campaign:
        new_data.append(vk.ads.getStatistics(account_id=id,
                                        ids_type=ids_type,
                                        ids=c['id'],
                                        period='day',
                                        date_from=date_start,
                                        date_to=date_end))
    return new_data


def data_preparation(campaigns, ids_type):
    arr = []
    for campaign in campaigns:
        # Создаём DataFrame со статистикой каждой кампании
        df2 = pd.DataFrame(campaign[0]['stats'])
        # Если статистика пустая, пропускаем.
        try:
            # Определяем индексы - датой
            df2.index = pd.DatetimeIndex(df2.day)
            # Добавляем в индекс весь список дат: от начальной к конечной
            df2 = df2.reindex(pd.date_range(df2.index.min(), df2.index.max()), fill_value=0.0)
            del df2['day']
            df2.insert(0, 'account_id', campaign[0]['id'])
            #df2.insert(1, "name", campaign[0]['id'])
            arr.append(df2)
        except AttributeError:
            pass
    df = pd.concat(arr)
    df = df.fillna(0)
    df.index.names = ['day']
    df.to_csv(f"{ids_type}.csv")
    return df

# Отображение графика
def show_graphic():
    df = pd.read_csv('df.csv')
    print(df)
    accounts = df.account_id.unique()
    plt.subplots(2, 1)
    plt.style.use('seaborn')
    plt.figure(figsize=(6, 6))
    plt.subplot(211)
    for account in accounts:
        y = df[df.account_id == account]["spent"].to_numpy()
        x = df[df.account_id == account]["day"].to_numpy()
        plt.plot(x, y, label=f"РК: {account}")
        #plt.xticks([::5], y[::5], fontsize=7)

    plt.ylabel('Затраты (руб.)')
    plt.legend()

    plt.subplot(212)
    for account in accounts:
        y = df[df.account_id == account]["clicks"].to_numpy()
        x = df[df.account_id == account]["day"].to_numpy()
        plt.plot(x, y, linestyle='--')

    plt.ylabel('Клики')
    plt.xlabel('Дни')


    plt.subplots_adjust(wspace=0, hspace=0.05)
    plt.style.use('seaborn')
    plt.show()


id = #Сюда нужно вставить ID
date_start = '2022-01-18'
date_end = '2022-02-27'
campaigns = get_campaigns(id)
ads = get_ads(id, campaigns)
campaign_stat = get_stat(id, campaigns, date_start, date_end, ids_type='campaign')
ads_stat = get_stat(id, ads, date_start, date_end, ids_type='ad')

campaigns_frame = data_preparation(campaign_stat, ids_type='campaign')
ads_frame = data_preparation(ads_stat, ids_type='ad')
df = pd.read_csv('df.csv')
print(df)
show_graphic()
