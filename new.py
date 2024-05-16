import requests
from bs4 import BeautifulSoup
import mysql.connector
import time

# Start URL
start_url = 'https://medex.com.bd/brands?page=1'

# Create a session to persist cookies
session = requests.Session()

# Set headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

# Connect to MySQL database
conn = mysql.connector.connect(
    host="host",
    user="username",
    password="password",
    database="database"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS medicines 
                  (id INT AUTO_INCREMENT PRIMARY KEY, medicine_name VARCHAR(255), generic_name VARCHAR(255), 
                  strength VARCHAR(255), manufacturer VARCHAR(255), price VARCHAR(255))''')

# Function to scrape data from a single page
def scrape_medex(url, session, headers):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        res = soup.find_all("div", {"class": "row"})[1]
        res = res.find_all("div", {"class": "col-xs-12 col-sm-6 col-lg-4"})
        for r in res:
            items = r.find_all("a", class_="hoverable-block")
            for item in items:
                href = item.get('href')
                scrape_and_save_product_details(href)
    else:
        print("Failed to fetch the page")

# Function to scrape details of a product from its URL and save to database
def scrape_and_save_product_details(url):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        medicine_name = soup.select_one('h1.page-heading-1-l.brand').text.strip()
        generic_name = soup.select_one('div[title="Generic Name"] > a').text.strip()
        strength = soup.select_one('div[title="Strength"]').text.strip()
        manufacturer = soup.select_one('a.calm-link').text.strip()
        price = soup.select_one('.package-container.mt-5.mb-5').text.strip()

        # Insert into database
        cursor.execute("INSERT INTO medicines (medicine_name, generic_name, strength, manufacturer, price) VALUES (%s, %s, %s, %s, %s)",
                       (medicine_name, generic_name, strength, manufacturer, price))
        conn.commit()

# Scrape data from multiple pages
for page in range(1, 10):
    url = f'https://medex.com.bd/brands?page={page}'
    scrape_medex(url, session, headers)
    time.sleep(5)  # Wait for 5 seconds to avoid overwhelming the server

# Close database connection
conn.close()
