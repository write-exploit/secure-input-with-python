from flask import Flask,request,Blueprint
import time
import random
import sqlite3

db_name = 'users.db' # database dosyanın adı bu dosyaya kullanıcıları ekliycez

# githubdan aldığım payloadlar
xss_payload = open(r"xss.txt",'r',encoding='utf8').read().splitlines() 
sql_payload = open(r"sql.txt",'r',encoding='utf8').read().splitlines()

# ===========================
# paylodları direk aldığımız gibi kullanmak pek içime sinmedi paylodları direk kullanırsak kullandığımız payloadlar tespit edilebilir o yüzden indexleri karıştırıcaz
xss_index = list()
[xss_index.append(i) for i in range(len(xss_payload))]
random.shuffle(xss_index) # indexlerin yerlerini karıştırıyoruz
# ===========================
sql_index = list()
[sql_index.append(i) for i in range(len(sql_payload))]
random.shuffle(sql_index)
# ===========================
karakterler = "! \' ^ # + $ % & / { ( [ } ) ] ? * \\ , ` : | ´ < > \" . : - _".split() # engellediğimiz karakterler

# any fonksiyonu sayesinde döngü icinde bir tane bile True değeri varsa sonuç olarak bize True değerini döndürür

# bu yazım tarzı zor geldiyse chatgpt'den normal halini alabilirsiniz

özel_karakter_kontrol = lambda girilen_deger: any(i for i in karakterler if i in girilen_deger) # özel karakterlerden biri girilen değerin içindeyse

xss_kontrol = lambda girilen_deger: any(xss_payload[i] for i in xss_index if xss_payload[i] == girilen_deger) # girilen değer xss paylodına eşitse

sql_kontrol = lambda girilen_deger: any(sql_payload[i] for i in sql_index if sql_payload[i] == girilen_deger) # girilen değer sql payloadına eşitse
# ===========================
def tara(orjinal_input): # zararlı girdi tespit edilirse devam_dur değişkenini dur'a eşitliycez ve sql sorgusu yapmıycaz ama sql sorgusu yapmış gibi sonuç döndürücez
    zamanı_artır = 0
    devam_dur = "devam"
    input_incele = orjinal_input.split()
    if len(input_incele) > 1: # 1 elemandan fazla ise demek (yani boşluklu girdi yapıldıysa ama bu boşluk sağdaki ve soldaki önemsiz boşluklar değil 'mer haba' tarzı boşlukdan bahsediyorum) 
        devam_dur = "dur"
        zamanı_artır = 0.003 # ilk denemede zararlı girdi bulunduysa 3ms'lik bir bekleme süresi ekliycez
    else:
        if özel_karakter_kontrol(orjinal_input):
            devam_dur = "dur"
            zamanı_artır = 0.002 # 2ms bekleme süresi
        else:
            if xss_kontrol(orjinal_input):
                devam_dur = "dur"
                zamanı_artır = 0.001 # 1ms bekleme süresi
            else:
                if sql_kontrol(orjinal_input): # burasıda çalışırsa zaten kodun en uzun çalışma süresindeki hali kullanıcıya yansımış olur yani süreyi artırmaya gerek yok
                    devam_dur = "dur"
                    zamanı_artır = 0
    return devam_dur,zamanı_artır
# =====================
second = Blueprint("second",__name__)
@second.route("/register/", methods=['GET', 'POST'])
def register_sayfası():
    register_mesaj = ""
    if request.method=='POST': # post işlemi yapıldıysa yani input değerleri girilip enter'a yada gönder'e basıldıysa burası çalışcak
        # return kısmındaki name değerlerini çekicez
        username = request.form['username'] # name="username"  kısmına girilen değeri çekiyoruz
        password = request.form['password'] # name="password"  kısmına girilen değeri çekiyoruz
        
        username = username.strip() # sağdaki soldaki gereksiz boşlukları kaldırıyoruz
        password = password.strip()

        if not username or not password: # kullanıcının boş bıraktığı input alanı varsa
            register_mesaj = "lütfen tüm alanları doldurun"
            # kullanıcı boş girdi yaptıysa beklemeden cevap verebiliriz herhangi bir sorun olmaz
        else:
            
            devam_dur,zamanı_artır = tara(username) # güvenlik taraması
            rastgele_süre = random.uniform(0,zamanı_artır) # fonksiyonun bize döndürdüğü zaman 3ms diyelim 0 ile 3ms arasından rastgele bir süre alıp o zaman kadar bekleme yapıcaz
            
            if devam_dur == "dur": # zararlı girdi tespit edildiyse devam_dur değişkeni dur'a eşitlenir eğer dur'a eşitlendiyse mesajımızı veriyoruz 
                # ve alt tarafta zamanın geçmesini bekleyip zaman geçtikten sonra return tarafında cevabımızı kullanıcıya döndürüyoruz
                register_mesaj = "kullanıcı ve password değerlerinde özel karakter ve boşluk kullanmayın"
            else:
                # username'de ve password'da herhangi bir sorun yoksa buraları çalıştıracaz

                baglan = sqlite3.connect(db_name) # database'e bağlanıyoruz
                cursor = baglan.cursor()

                kullanici_mevcutmu = f"SELECT COUNT(*) FROM users WHERE name = '{username}';" # kullanıcı database'de varmı kontrol ediyoruz eğer yoksa 0 değeri döner
                cursor.execute(kullanici_mevcutmu) # execute, sql komutunu çalıştırır
                
                if cursor.fetchall()[0][0] == 0: # kullanıcı yoksa
                    kullanici_ekle = f"INSERT INTO users VALUES ('{username}','{password}');" # kullanıcıyı ekliyoruz
                    cursor.execute(kullanici_ekle)
                    baglan.commit()
                    register_mesaj = "kullanıcı oluşturuldu"
                else:
                    register_mesaj = "bu kullanıcı mevcut"
                cursor.close() # bağlantıları kapatıyoruz
                baglan.close()
            time.sleep(rastgele_süre) # rastgele süre kadar beliyoruz
    return '''
        <style>
        h2 {text-align: center}
        form {text-align: center}
        </style>

        <h2>kullanıcı oluşturun</h2>
        <br>
        <form id="gönder" action="/register/" method="POST">
        <input type="text" name="username">
        <input type="password" name="password">
        <input type="submit" value="gönder">
        </form>
        <br>
        '''+'''
        <h2>{}</h2>
        '''.format(register_mesaj)
# ========================
second1 = Blueprint("second1",__name__)
@second1.route("/login/", methods=['GET', 'POST'])
def login_sayfası():
    login_mesaj = ""
    if request.method=='POST':
        username = request.form['username']
        username = username.strip() # sql sorgusunda girilen input değerinde boşluk varsa doğru sonuç dönmez o yüzden boşlukları kaldırıp sql sorgusuna öyle dahil ediyoruz
        if not username:
            login_mesaj = "kullanıcı mevcut değil"
            # username tarafına bir girdi yapılmadıysa yine beklememize gerek yok direk cevap döndürücez
        else:
            devam_dur,zamanı_artır = tara(username)
            
            rastgele_süre = random.uniform(0,zamanı_artır)

            if devam_dur == "dur":
                login_mesaj = "kullanıcı mevcut değil"
            else:
                baglan = sqlite3.connect(db_name)
                cursor = baglan.cursor()
                
                kullanici_bilgisi = f"SELECT * FROM users WHERE name = '{username}';" # kullanıcı bilgilerini çeken bir kod
                cursor.execute(kullanici_bilgisi)
                rows = cursor.fetchall()
                if not rows: # kullanıcı mevcut değilse boş bir liste gelir
                    login_mesaj = "kullanıcı mevcut değil"
                else: # kullanıcı mevcutsa bilgiler liste içinde gelir
                    rows = rows[0]
                    login_mesaj = rows # kullanıcı bilgileri
                cursor.close()
                baglan.close()
            time.sleep(rastgele_süre) # rastgele süre kadar bekliyoruz
            # ve bekleme sonrasında return ile sayfamızı döndürüyoruz
    return '''
        <style>
        h2 {text-align: center}
        form {text-align: center}
        </style>
        <h2>şifrenizi öğrenin</h2>
        <br>
        <form id="gönder" action="/login/" method="POST">
        <input type="text" name="username">
        <input type="submit" value="gönder">
        </form>
        <br>
        '''+'''
        <h2>{}</h2>
        '''.format(login_mesaj)
