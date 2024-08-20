import pandas as pd
from instagrapi import Client
from datetime import datetime
import time as tm
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from getpass import getpass

def get_caption_from_file(id):
    txt_file = os.path.join('texts', f"{id}.txt")
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    return f"ID: {id} resmi"  # Eğer txt dosyası yoksa, ID bilgisini kullan

def upload_to_instagram(cl, image_path, caption):
    cl.photo_upload(image_path, caption)

def upload_to_linkedin(driver, caption, image_path):
    # LinkedIn feed sayfasına gidin
    driver.get("https://www.linkedin.com/feed/")
    tm.sleep(5)

    # Medya ekle butonuna tıklayın
    media_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Medya ekle")]')
    media_button.click()
    tm.sleep(5)

    # Dosya yükleme inputunu bulun ve resim dosyasını yükleyin
    file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    file_input.send_keys(os.path.abspath(image_path))
    tm.sleep(5)

    # İleri butonuna tıklayın
    next_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "İleri")]')
    next_button.click()
    tm.sleep(5)

    # Açıklama alanına metni girin
    content_div = driver.find_element(By.CSS_SELECTOR, 'div.ql-editor[aria-label="İçerik oluşturma için metin düzenleyici"]')
    content_div.click()
    content_div.send_keys(caption)
    tm.sleep(5)

    # Gönderi butonuna tıklayın
    post_button = driver.find_element(By.CSS_SELECTOR, '.share-actions__primary-action.artdeco-button.artdeco-button--2.artdeco-button--primary')
    post_button.click()

    tm.sleep(50)

def check_and_upload(cl, driver):
    # CSV dosyasını oku
    df = pd.read_csv('veri.csv')

    # Verileri ayrıştır
    df[['Date', 'Time']] = df['Dates'].str.split(', ', expand=True)
    
    # Tarih ve saat sütunlarını birleştir ve datetime formatına dönüştür
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format="%m/%d/%Y %H:%M")

    while True:
        now = datetime.now()

        for index, row in df.iterrows():
            scheduled_time = row['Datetime']

            # Zamanı tam olarak kontrol et
            if now >= scheduled_time and now < scheduled_time + pd.Timedelta(minutes=1):
                id = row['Index']
                image_path = os.path.join('images', f"{id}.png")
                if os.path.exists(image_path):
                    caption = get_caption_from_file(id)  # Dosyadan açıklama al
                    upload_to_instagram(cl, image_path, caption)
                    upload_to_linkedin(driver, caption, image_path)
                    df.drop(index, inplace=True)  # Yüklenen resimleri kaldır
                    df.to_csv('veri.csv', index=False)  # CSV dosyasını güncelle
        tm.sleep(60)  # Her 60 saniyede bir kontrol et

if __name__ == "__main__":
    # Kullanıcı bilgilerini al
    insta_username = input("Instagram kullanıcı adı: ")
    insta_password = getpass("Instagram şifre: ")
    
    linkedin_username = input("LinkedIn kullanıcı adı: ")
    linkedin_password = getpass("LinkedIn şifre: ")

    # Instagram'a giriş yap
    cl = Client()
    cl.login(insta_username, insta_password)

    # LinkedIn'e giriş yap ve oturumu açık tut
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/login")
    tm.sleep(2)
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    
    username_field.send_keys(linkedin_username)
    password_field.send_keys(linkedin_password)
    driver.find_element(By.XPATH, '//*[@type="submit"]').click()
    tm.sleep(3)

    # Güvenlik kontrolünü kontrol et
    try:
        security_check = driver.find_element(By.XPATH, '//h1[text()="Hızlıca bir güvenlik kontrolü yapalım"]')
        if security_check:
            print("Güvenlik kontrolü bulundu, doğrulamayı yapıp enter tuşuna basın...")
            input("Devam etmek için enter tuşuna basın...")
    except:
        pass

    # Gönderileri kontrol et ve paylaş
    check_and_upload(cl, driver)

    def get_latest_instagram_post(cl):
    # Kullanıcının en son gönderisini alın
    user_id = cl.user_id_from_username(insta_username)
    posts = cl.user_medias(user_id, 1)
    if posts:
        return posts[0]
    else:
        print("Gönderi bulunamadı.")
        return None

def get_instagram_comments(cl, post_id):
    # Gönderideki yorumları al
    comments = cl.media_comments(post_id)
    for comment in comments:
        print(f"{comment.user.username}: {comment.text}")

def reply_to_instagram_comment(cl, post_id):
    # Terminalden kullanıcıya yorum yazdır
    comment_text = input("Instagram'da cevap vermek için bir yorum yazın: ")
    cl.media_comment(post_id, comment_text)
    print("Instagram'da yorum gönderildi.")

def post_comment_on_linkedin(driver, post_id):
    # LinkedIn'de gönderiye yorum yap
    comment_text = input("LinkedIn'de cevap vermek için bir yorum yazın: ")
    comment_box = driver.find_element(By.XPATH, f"//div[@data-id='{post_id}']//div[@contenteditable='true']")
    comment_box.click()
    comment_box.send_keys(comment_text)
    post_button = driver.find_element(By.XPATH, f"//div[@data-id='{post_id}']//button[contains(@class, 'comments-comment-box__submit-button')]")
    post_button.click()
    print("LinkedIn'de yorum gönderildi.")

if __name__ == "__main__":
    # Mevcut iş akışınıza göre bu kısımları çalıştırabilirsiniz
    # Instagram'da en son gönderiye yorum çekme ve cevap verme
    latest_post = get_latest_instagram_post(cl)
    if latest_post:
        post_id = latest_post.id
        print("Instagram'daki en son gönderinin yorumları:")
        get_instagram_comments(cl, post_id)
        reply_to_instagram_comment(cl, post_id)

    # LinkedIn'de yorum çekme ve cevap verme
    linkedin_post_id = "YOUR_LINKEDIN_POST_ID"  # Bunu uygun bir şekilde belirlemelisiniz
    post_comment_on_linkedin(driver, linkedin_post_id)

    # İşlem bittiğinde WebDriver'ı kapatın
    driver.quit()