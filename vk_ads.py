import vk_api
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

token = '451a4fe3e879c46a5b879dc41a78962a02419827a12aab22ce132810fa6c677f7ba80660ddb54d2819876'

session = vk_api.VkApi(token=token)
vk = session.get_api()

# Получаем список кампаний по id рекламного аккаунта
def get_campaigns(id):
    camp = vk.ads.getCampaigns(account_id=id)
    return camp

# Для каждой рекламной кампании выгружаем статистику
def get_ads_account(id, campaign, date_start, date_end):
    new_data = []

    for c in campaign:
        new_data.append(vk.ads.getStatistics(account_id=id,
                                        ids_type='campaign',
                                        ids=c['id'],
                                        period='day',
                                        date_from=date_start,
                                        date_to=date_end))
    return new_data


def data_preparation(campaigns):
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
    df.to_csv('df.csv')
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


#id = 1607207085
#date_start = '2022-01-18'
#date_end = '2022-02-27'
#campaigns = get_campaigns(id)
#ads = get_ads_account(id, campaigns, date_start, date_end)
#data_frame = data_preparation(ads)
show_graphic()



