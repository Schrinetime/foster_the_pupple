import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

adoption_key = 'adoption'
search_locs = [(adoption_key, "https://cincinnatianimalcare.org/adopt/available-dogs/"),
               ('lost&found', "https://cincinnatianimalcare.org/lost-found/")
                ]

dog_list = []
for (status, url) in search_locs:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    src = soup.find('iframe')['data-src']
    # print(src)

    r = requests.get(src)
    s = BeautifulSoup(r.content, 'html.parser')

    dog_soup = {a.parent.parent.parent for a in s.find_all(text="Dog")}

    for dog_info in dog_soup:
        dog = {}
        dog['id'] = dog_info.find("div", class_="list-animal-id").text
        dog['name'] = dog_info.find("div", class_="list-animal-name").text
        dog['breed'] = dog_info.find("div", class_="list-animal-breed").text
        dog['sex'] = dog_info.find("div", class_="list-animal-sexSN").text
        dog['age'] = dog_info.find("div", class_="list-animal-age").text
        dog['status'] = status
        if status == adoption_key:
            dog['loc'] = dog_info.find("div", class_="hidden").text
        dog_list.append(dog)
        # print(dog_list)

dogFrame = pd.DataFrame(dog_list)
dogFrame.set_index('id', inplace=True)

ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
dogFrame.to_csv(f"{ts}.csv")