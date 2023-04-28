import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def get_ceo_or_founder_email(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    email = ""
    
    # Look for specific text that indicates a CEO or founder
    for tag in soup.find_all('strong'):
        if "CEO" in tag.text or "Founder" in tag.text:
            email_tag = tag.find_next_sibling()
            if email_tag and (email_tag.name == 'a' and email_tag.has_attr('href')):
                email = email_tag['href'].replace('mailto:', '').strip()
                break
            elif email_tag and re.match(r"[^@]+@[^@]+\.[^@]+", email_tag.text):
                email = email_tag.text.strip()
                break

    # If email not found, search for a "Leadership" or "About Us" section
    if not email:
        for section in soup.find_all('section'):
            if "Leadership" in section.text or "About Us" in section.text:
                for tag in section.find_all('a'):
                    if tag.has_attr('href') and re.match(r"[^@]+@[^@]+\.[^@]+", tag['href']):
                        email = tag['href'].replace('mailto:', '').strip()
                        break
                if email:
                    break

    # If email not found, search for a "Contact Us" page
    if not email:
        for link in soup.find_all('a'):
            if "Contact" in link.text:
                contact_url = link['href']
                if not contact_url.startswith('http'):
                    contact_url = urljoin(url, contact_url)
                res_contact = requests.get(contact_url)
                soup_contact = BeautifulSoup(res_contact.content, 'html.parser')
                for tag in soup_contact.find_all('a'):
                    if tag.has_attr('href') and re.match(r"[^@]+@[^@]+\.[^@]+", tag['href']):
                        email = tag['href'].replace('mailto:', '').strip()
                        break
                if email:
                    break
    
    # If email still not found, use the original function to look for any email
    if not email:
        email = get_email(url)
    
    return email

df = pd.read_csv("website2.csv")

emails = []
for url in df["Website"]:
    ceo_email = get_ceo_or_founder_email(url)
    emails.append(ceo_email)

df["Email"] = emails

print(df.to_csv(index=False))
