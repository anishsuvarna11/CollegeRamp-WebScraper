import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def get_email(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    email = ""
    for link in soup.find_all('a'):
        if link.has_attr('href') and (link['href'].startswith('mailto:') or re.match(r"[^@]+@[^@]+\.[^@]+", link['href'])):
            email = link['href'].replace('mailto:', '').strip()
            break
    return email

def get_ceo_email(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    email = ""
    for tag in soup.find_all('strong'):
        if "CEO" in tag.text or "Founder" in tag.text:
            email_tag = tag.find_next_sibling()
            if email_tag and (email_tag.name == 'a' and email_tag.has_attr('href')):
                email = email_tag['href'].replace('mailto:', '').strip()
                break
            elif email_tag and re.match(r"[^@]+@[^@]+\.[^@]+", email_tag.text):
                email = email_tag.text.strip()
                break
    return email

df = pd.read_csv("website2.csv")

emails = []
for url in df["Website"]:
    ceo_email = get_ceo_email(url)
    if ceo_email:
        emails.append(ceo_email)
    else:
        email = get_email(url)
        emails.append(email)

df["Email"] = emails

print(df.to_csv(index=False))
