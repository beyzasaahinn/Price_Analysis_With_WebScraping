##### TARAYICIYI KONFİGÜRE ETME VE BAŞLATMA #####

#1.Selenium'un WebDriver sınıfını kullanarak bir adet 'options' adında ChromeOptions tanımlama
from selenium import webdriver
options = webdriver.ChromeOptions()

#2. Tanımlanan options'a tam ekran özelliği ekleme
options.add_argument("--start-maximized")

#3.Hazırlanan options'u kullanarak driver adında bir adet chrome taryıcısı oluşturma
driver = webdriver.Chrome(options)



##### ANA SAYFAYI İNCELEME VE KAZIMA #####

#1.Ana sayfayı driver ile açma
import time
SLEEP_TIME = 2

driver.get("https://books.toscrape.com/")
time.sleep(SLEEP_TIME)

#2."Travel" ile "Nonfiction" kategori sayfalarının linklerini tutan elementleri tek seferde bulan XPath sorgusunu yazma
category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

#3.XPath sorgusu ile yakalanan elementleri driver'ı kullanarak bulma ve kategori detay linklerini kazıma
from selenium.webdriver.common.by import By
category_elements = driver.find_elements(By.XPATH, category_elements_xpath)

category_urls = [element.get_attribute("href") for element in category_elements]
print(category_urls)


##### KATEGORİ SAYFASININ İNCELENMESİ VE KAZINMASI #####

#1.Herhangi bir detay sayfasına girip o sayfadaki kitapların detay linkini tutan elementleri yakalayan XPath sorgusunu yazma
driver.get(category_urls[0])
time.sleep(SLEEP_TIME)
book_elements_xpath = "//div[@class='image_container']//a"

#3.Driver ile XPath sorgusunu kullanarak elementleri yakalama ve detay linklerini çıkarma
book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
book_urls = [element.get_attribute("href") for element in book_elements]
print(book_urls)
print(len(book_urls))

#3.Sayfalandırma (Pagination) için butonlara tıklamak yerine sayfa linkini manipüle etme işlemi
## İpucu: (Sayfa değiştikçe URL'de ne değişiyor gözlemlemek önemli)
### --> fark edilecek ki tek sayfalarda url index.html, .ok sayfalarda page-i.html !!
MAX_PAGINATION = 3
url = category_urls[0]
book_urls = []

for i in range(1, MAX_PAGINATION):
    update_url = url if i == 1 else url.replace("index", f"page-{i}")  # Sayfa URL'sini güncelle
    driver.get(update_url)  # Güncellenmiş URL'yi aç

    book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

    temp_urls = [element.get_attribute("href") for element in book_elements]
    book_urls.extend(temp_urls)  # URL'leri ana listeye ekle

    print(book_urls)
    print(len(book_urls))
    # url = category_urls[0] indexi değiştirerek gözlem yapılabilir.

#4.Sayfalandırmanın sonuna geldiğinizi anlamak adına kategorinin 999. sayfasına giderek çıkan sayfayı inceleme
## İpucu: (.../category/books/nonfiction_13/page-999.html)
### Dikkat: (.../category/books/travel_2/page-1.html ???????)

#5.Bir önceki adımdaki incelemenin sonucunda sayfalandırmada sonsuz döngüye girmemek adına kontrol kullanma
## İpucu: (text'inde 404 içeren bir h1 var mı?) veya (if not product_list) ya da (len(product_list) <= 0)
MAX_PAGINATION = 3
url = category_urls[0]
book_urls = []

for i in range(1, MAX_PAGINATION):
    update_url = url if i == 1 else url.replace("index", f"page-{i}")
    driver.get(update_url)

    book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
    if not book_elements:
        break
    temp_urls = [element.get_attribute("href") for element in book_elements]
    book_urls.extend(temp_urls)

    print(book_urls)
    print(len(book_urls))


##### ÜRÜN DETAY SAYFASININ KAZINMASI #####
#1.Herhangi bir ürünün detay sayfasına girip class attribute'u content olan div elementini yakalama
driver.get(book_urls[0])
time.sleep(SLEEP_TIME)
content_div = driver.find_elements(By.XPATH, "//div[@class='content']")

#2.Yakalanan divin HTML'ini alma ve inner_html adlı değişkene atama
inner_html = content_div[0].get_attribute("innerHTML")

#3.inner_html ile soup objesi oluşturma
from bs4 import BeautifulSoup
soup = BeautifulSoup(inner_html, "html.parser")

#4.Oluşturulan soup objesi ile şu bilgileri kazıma:
#Kitap adı
name_elem = soup.find("h1")
book_name = name_elem.text

#Kitap Fiyatı
# Kitap Fiyatını Bulma
price_elem = soup.find("p", attrs={"class": "price_color"})
book_price = price_elem.text

#Kitabın yıldız sayısını bulma
## İpucu : regex = re.compile('^star-rating ')
import re
regex = re.compile('^star-rating ')
star_elem = soup.find("p", attrs={"class": regex})
print(star_elem)
book_star_count = star_elem["class"][-1]

#Kitap Açıklaması
desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
book_desc = desc_elem.text

#Product Information başlığı altında kalan tablodaki bilgiler
product_info = {}
table_rows = soup.find("table").find_all("tr")
for row in table_rows:
    key = row.find("th").text  #
    value = row.find("td").text
    product_info[key] = value  # Sözlüğe anahtar-değer çifti olarak ekleme



##### FONKSİYONLAŞTIRMA VE TÜM SÜRECİ OTOMATİZE ETME #####

#1.İşlemleri fonksiyonlaştırma. Örnek olarak : def get_product_detail(driver):   |    def get_category_detail_urls(driver)
def get_book_detail(driver, url):
    """
    Gets book data from given book detail page URL
    """
    driver.get(url)
    time.sleep(SLEEP_TIME)

    content_div = driver.find_elements(By.XPATH, "//div[@class='content']")
    inner_html = content_div[0].get_attribute("innerHTML")

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(inner_html, "html.parser")

    name_elem = soup.find("h1")
    book_name = name_elem.text

    price_elem = soup.find("p", attrs={"class": "price_color"})
    book_price = price_elem.text

    import re
    regex = re.compile("^star-rating ")
    star_elem = soup.find("p", attrs={"class": regex})
    book_star_count = star_elem["class"][-1]

    desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
    book_desc = desc_elem.text

    product_info = {}
    table_rows = soup.find("table").find_all("tr")
    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value

    return {
        "book_name": book_name, "book_price": book_price, "book_star_count": book_star_count,
        "book_desc": book_desc, **product_info}  #book_desc'den sonra yazmaya devam et demek {{}} olmaması adına


def get_book_urls(driver, url):
    """
    Gets book URLs from given page URL
    """
    MAX_PAGINATION = 3
    book_urls = []
    book_elements_xpath = "//div[@class='image_container']//a"

    for i in range(1, MAX_PAGINATION):
        updated_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(updated_url)
        time.sleep(SLEEP_TIME)

        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

        if not book_elements:
            break

        # Bulunan elementlerden href değerlerini çıkar
        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)

    return book_urls

def get_travel_and_nonfiction_category_urls(driver, url):
    """
    Gets category URLs from given homepage URL
    """
    driver.get(url)
    time.sleep(SLEEP_TIME)

    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    category_urls = [element.get_attribute("href") for element in category_elements]

    return category_urls


def initialize_driver():
    """
    Initializes driver with maximized option
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

#2.Süreci otomatize ederek Travel ile Nonfiction kategorilerine ait tüm kitapların detaylarını alacak şekilde kodu düzenleme
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

SLEEP_TIME = 0.25

def main():
    BASE_URL = "https://books.toscrape.com/"
    driver = initialize_driver()
    category_urls = get_travel_and_nonfiction_category_urls(driver, BASE_URL)
    data = []

    for cat_url in category_urls:
        book_urls = get_book_urls(driver, cat_url)
        for book_url in book_urls:
            book_data = get_book_detail(driver, book_url)
            book_data["cat_url"] = cat_url
            data.append(book_data)

    print(len(data))

### OPSİYONEL OLARAK ###
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", 40)
pd.set_option("display.width", 2000)
df = pd.DataFrame(data)

return df

# Ana fonksiyondan dönen DataFrame'i al
df = main()
print(df.head())
print(df.shape)









