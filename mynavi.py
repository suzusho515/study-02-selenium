import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
        options = ChromeOptions()
    else:
        print("driverがchromeではない")
        options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
    # options.add_argument('log-level=3')
    #options.add_argument('--ignore-certificate-errors')
    #options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        #return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
        #chromedriverの自動更新用
        return Chrome(ChromeDriverManager().install(), options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

# ログ処理
def log(message):
    logMessage = message
    # ログ出力
    with open("log_file.log", 'a', encoding='utf-8_sig') as f:
        f.write(logMessage + '\n')
    print(logMessage)

# input_search_keyword
def input_search_keyword():
    print('検索したいワードを入力してください')
    search_keyword = input('>> ')
    log("keyword_input完了")
    return search_keyword

# main処理
def main():
    #検索ワードを取得
    search_keyword = input_search_keyword()

    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    log("URL遷移完了")
    sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓に入力
    driver.find_element_by_css_selector(
        "input.topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_css_selector(
        "button.topSearch__button").click()

    #出力用のリスト作成
    name_list = []
    place_list = []
    salary_list = []

    #ページカウント

    # ページ終了まで繰り返し取得    
    while True:
        # 会社名が入った、h3タグを取得
        name_get = driver.find_elements_by_xpath("//h3[contains(@class, 'cassetteRecruit')]")
        #勤務地と初年収が入った、tableタグを取得
        table_get = driver.find_elements_by_css_selector("table.tableCondition")

        #会社名の取得
        for name in name_get:
            #会社名をリストに追加
            name_list.append(name.text)
        
        #勤務地と初年度年収の取得
        for table in table_get:

            detail_table = table.find_elements_by_css_selector("tr > th")
            #"勤務地","初年度年収"で検索
            #記載がない場合は、Noneと書き込むための比較値
            count_place_list = len(place_list)
            count_salary_list = len(salary_list)
            
            #エラーで取得できなくても、空の値を追加
            try:    
                for detail in detail_table:
                    if detail.text == "勤務地":
                        place = detail.find_element_by_xpath('..').find_element_by_css_selector("td")
                        place_list.append(place.text)

                    elif detail.text == "初年度年収":
                        salary = detail.find_element_by_xpath('..').find_element_by_css_selector("td")
                        salary_list.append(salary.text)
            except Exception as e:
                log(e)
                log("エラー発生")
            
            finally:    
                #追加が無かったらNoneと書き込む
                if count_place_list == len(place_list):
                    place_list.append(None)
                if count_salary_list == len(salary_list):
                    salary_list.append(None)
        
        log("ページ内取得完了")


        #次のページへ遷移
        try:
            next_button = driver.find_element_by_css_selector("a.iconFont--arrowLeft")
            next_url = next_button.get_attribute("href")
            driver.get(next_url)
            sleep(5)
        except Exception:
            log("最終ページ")
            break

    #Dataframeへ追加前の確認
    print(len(name_list))
    print(len(place_list))
    print(len(salary_list))

    # DataFrameに対して辞書形式でデータを追加する
    df = pd.DataFrame(
        {"会社名": name_list,
         "勤務地": place_list,
         "初年度年収": salary_list}
        )

    df.to_csv("result.csv", index=None, encoding="utf-8-sig")
        
        
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
