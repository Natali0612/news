import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta
from tqdm import tqdm

# Файл для логирования
log_file = "news_log.txt"

# Словарь для хранения уже обработанных статей
processed_articles = {}


# Функция для извлечения и логирования новостей
def fetch_and_log_news():
    url = 'https://edition.cnn.com/politics/congress'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Превышено время ожидания. Сервер слишком долго не отвечает.")
        return
    except requests.exceptions.TooManyRedirects:
        print("Слишком много перенаправлений. Возможно, URL указан неверно.")
        return
    except requests.exceptions.RequestException as e:
        print(f"Не удалось получить доступ к веб-странице. Ошибка: {e}")
        return

    if response.status_code != 200:
        print(f"Не удалось получить доступ к веб-странице. Код состояния: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'lxml')

    articles = soup.find_all('article')
    new_articles_found = False

    for article in articles:
        title_tag = article.find('h3')
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = article.find('a', href=True)['href']
        description_tag = article.find('p')
        description = description_tag.get_text(strip=True) if description_tag else "Описание отсутствует"

        if 'Republican' in title or 'Democratic' in title or 'Republican' in description or 'Democratic' in description:
            if link not in processed_articles:
                processed_articles[link] = title

                authors = "Неизвестно"  # Можно расширить извлечение авторов, если это требуется

                # Логирование в файл
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Время: {datetime.now()}\n")
                    f.write(f"Заголовок: {title}\n")
                    f.write(f"Описание: {description}\n")
                    f.write(f"Авторы: {authors}\n")
                    f.write(f"Ссылка: {link}\n")
                    f.write(f"------------------------------\n")



    if not new_articles_found:                # # Отображение в консоли
                # print(f"Время: {datetime.now()}")
                # print(f"Заголовок: {title}")
                # print(f"Описание: {description}")
                # print(f"Авторы: {authors}")
                # print(f"Ссылка: {link}")
                # print("------------------------------")
                # new_articles_found = True
        print("На данный момент новых релевантных статей не найдено.")


# Запуск функции fetch_and_log_news каждые 15 минут
schedule.every(15).minutes.do(fetch_and_log_news)

# Время работы программы
total_duration_minutes = 4 * 60  # в минутах (укажите 4 часа)
end_time = datetime.now() + timedelta(minutes=total_duration_minutes)

# Показать прогресс-бар обратного отсчета
with tqdm(total=total_duration_minutes, desc="Оставшееся время", unit=" мин",
          bar_format="{desc}: {remaining} минут осталось") as pbar:
    while datetime.now() < end_time:
        schedule.run_pending()
        time_left_minutes = (end_time - datetime.now()).total_seconds() / 60
        pbar.n = total_duration_minutes - int(time_left_minutes)
        pbar.set_postfix_str(f"{int(time_left_minutes)} мин")
        pbar.refresh()
        time.sleep(60)

print("Завершена обработка новостей.")
