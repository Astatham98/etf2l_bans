import requests
import json
import pandas as pd

page_1 = 'https://api-v2.etf2l.org/bans?limit=100&page=1'
headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Dnt": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        }

def get_bans(request, ban_data=[]):
        bans = requests.get(request)
        print(bans.status_code)
        if bans.status_code == 429:
            print('too many requests sent.')
            return ban_data
        else:
            json_bans = None
            try:
                json_bans = bans.json()
            except json.decoder.JSONDecodeError as e:
                new_number = '=' + str(int(request.split('=')[-1]) + 1)
                
                next_page_split = request.replace('=' + request.split('=')[-1], new_number)
                next_page = ''.join([x for x in next_page_split])
                if next_page is not None:
                    return get_bans(next_page, ban_data)
                else:
                    return list(set(ban_data))
            
            if json_bans is not None:
                next_page = json_bans['bans']['next_page_url']
                data = json_bans['bans']['data']
                ban_data_new = [x['steamid64'] for x in data]
                ban_data = ban_data + ban_data_new
                print(len(ban_data))
                if next_page is not None:
                    return get_bans(next_page, ban_data)
                else:
                    return list(set(ban_data))
            else:
                return list(set(ban_data))
        
    
def get_player_details(ID, headers, session):
    
    data = session.get(f'https://api.etf2l.org/player/{ID}.json', headers=headers)
    if data.status_code ==200:
        data_json = data.json()
        player_data = data_json['player']
        
        reasons = [x['reason'] for x in player_data['bans']]
        country = player_data['country']
        name = player_data['name']
        
        dictionaries_list = []
        for reason in reasons:
            dictionaries_list.append({'ID': ID,
                                    'Name': name,
                                    'Country': country,
                                    'Reason': reason})
            
        return dictionaries_list
    else:
        print(data.status_code)
        return []

player_ids = get_bans(page_1)
player_dicts = []
req = requests.Session()
for i, ID in enumerate(player_ids):
    player_dicts += get_player_details(ID, headers, req)
    if i % 100 == 0:
        print(f"{i}/{len(player_ids)} IDs completed.")

df = pd.DataFrame(player_dicts)
print(df.head(20))
df.to_csv('output_150724.csv', index=False)
    




