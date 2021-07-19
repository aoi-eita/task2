import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
import datetime
from bs4 import BeautifulSoup



LOG_FILE_PATH = "./log/log_{datetime}.log"
EXP_CSV_PATH="./exp_list_{search_keyword}_{datetime}.csv"
log_file_path=LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
          options = ChromeOptions()
    else:
      options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(ChromeDriverManager().install(), options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

# ログの作成
def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s:%s] %s' % ('log',now,txt)
# ログの出力   
    with open(log_file_path , 'a' ,encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

# main処理

def main():
    log("処理開始")
    search_keyword =input("検索したいワードを入力して下さい >>> ")
    log(f"検索キーワード：{search_keyword}")
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    month_salary_list = []
    year_salary_list = []
    name_list = []
    count = 1
    success = 0
    fail = 0

    while True:
    # ソースコードを取得
        time.sleep(10)
    
     # HTMLをパースする
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser') 
    
    # 会社ブロック単位でitemsに格納
        items = soup.findAll(class_="cassetteRecruit__content")

    #try文でエラーを回避
    # forとtryを併用する時はtryを中に入れて使用　そうしないと止まってしまう

        for i in range(len(items)):
            try:
                name_list.append(items[i].findAll(class_="cassetteRecruit__name")[0].text.split("|")[0])
                month_salary_list.append(items[i].findAll(class_="tableCondition__body")[3].text)
                year_salary_list.append(items[i].findAll(class_="tableCondition__body")[4].text)
                log(f"{count}件目成功：{name_list[i]}")
                success+=1
            except Exception as e:
                year_salary_list.append("データなし")
                log(f"{count}件目失敗：{name_list[i]}")
                log(e)
                fail+=1
            finally:
                count+=1

        
        if len(driver.find_elements_by_class_name("iconFont--arrowLeft")) > 0:
            next_url = driver.find_elements_by_class_name("iconFont--arrowLeft")[0].get_attribute("href")
            driver.get(next_url)  
        else:
            log("終了しました")
            break
                
    # 空のDataFrame作成
    df = pd.DataFrame()

    # 1ページ分繰り返し
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    for (name,month_salary,year_salary) in zip(name_list,month_salary_list,year_salary_list):
        df = df.append(
        {"会社名": name,
        "月給": month_salary,
        "年収": year_salary},
        ignore_index=True)

    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword,datetime=
                                  now),encoding="utf-8-sig")
        
    log(f"処理完了 成功件数: {success} 件 / 失敗件数: {fail} 件")

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
