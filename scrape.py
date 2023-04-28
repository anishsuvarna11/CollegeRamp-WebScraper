import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import requests

def get_email(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    email = None

    # Look for email address in plain text
    text = soup.get_text()
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        email = email_match.group(0)
    
    # Look for email address in mailto link
    if not email:
        email_link = soup.find('a', href=re.compile(r'^mailto:'))
        if email_link:
            email = email_link['href'][7:]
    
    # Look for email address in contact form
    if not email:
        form = soup.find('form')
        if form:
            email_input = form.find('input', attrs={'type': 'email'})
            if email_input:
                email = email_input['value']
    
    # Look for email address in header or footer
    if not email:
        header = soup.find('header')
        footer = soup.find('footer')
        if header:
            email_link = header.find('a', href=re.compile(r'^mailto:'))
            if email_link:
                email = email_link['href'][7:]
        if footer and not email:
            email_link = footer.find('a', href=re.compile(r'^mailto:'))
            if email_link:
                email = email_link['href'][7:]
    
    # Look for email address on "About Us" page
    if not email:
        about_link = soup.find('a', text=re.compile(r'about', re.IGNORECASE), href=True)
        if about_link:
            about_url = about_link['href']
            about_r = requests.get(about_url)
            about_soup = BeautifulSoup(about_r.content, 'html.parser')
            about_text = about_soup.get_text()
            about_email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', about_text)
            if about_email_match:
                email = about_email_match.group(0)
    
    # Look for email address on "Team" page
    if not email:
        team_link = soup.find('a', text=re.compile(r'team', re.IGNORECASE), href=True)
        if team_link:
            team_url = team_link['href']
            team_r = requests.get(team_url)
            team_soup = BeautifulSoup(team_r.content, 'html.parser')
            team_email_links = team_soup.find_all('a', href=re.compile(r'^mailto:'))
            for link in team_email_links:
                text = link.get_text().lower()
                if 'ceo' in text or 'founder' in text or 'president' in text:
                    email = link['href'][7:]
                    break
    
    return email

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

input_file = 'website2.csv'
output_file = 'websites_with_emails.csv'

df = pd.read_csv(input_file)

df['Email'] = df['Website'].apply(get_email)

df.to_csv(output_file, index=False)
