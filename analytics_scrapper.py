import time
import pandas as pd
from lxml import etree
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

class AnalyticsScraper:
    def __init__(self):
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # 初始化WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 基础URL和等待超时时间
        self.base_url = "https://analytics.twire.gg/en/pubg/match-stats/1662770"
        self.wait = WebDriverWait(self.driver, 15)
    
    def fetch_player_stats(self):
        """获取指定轮次和分组的玩家统计数据"""
        # 构建完整URL
        url = self.base_url
        self.driver.get(url)
        print(f"正在获取页面: {url}")
        
        try:
            # 等待玩家表格加载完成
            table = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".kpPvTx"))
            )
            
            # 等待所有行加载完成
            time.sleep(10)  # 确保动态内容完全加载
            
            # 解析表格数据
            return self._parse_player_table(table)
            
        except Exception as e:
            print(f"获取数据时出错: {e}")
            return []

    def etree_after_click(self, html_source):
        time.sleep(5)
        page = Soup(html_source, features="html.parser")
        html_etree = etree.HTML(str(page))
        return html_etree
    
    def _parse_player_table(self, table_element):
        """解析玩家数据表格"""
        # 获取表格HTML
        table_html = table_element.get_attribute('outerHTML')
        
        # 使用BeautifulSoup解析
        etree = self.etree_after_click(table_html)
        t_header = etree.xpath("//thead//th[@class='sc-khIgEk hQhHpX']/text()")
        t_header = t_header[1:]
        t_header = [td for td in t_header if td != ' ']
        game_data = etree.xpath("//tbody//td/text()")

        players_data = []

        player_cnt = 0
        while player_cnt < 64:
            row_data = {}
            for i, title in enumerate(t_header):
                row_data[title] = game_data[i + len(t_header) * player_cnt]
            players_data.append(row_data)
            player_cnt += 1
        
        return players_data
    
    def export_to_csv(self, data, filename="player_stats.csv"):
        """将数据导出到CSV文件"""
        if not data:
            print("没有数据可导出")
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"数据已导出到 {filename}")
    
    def close(self):
        """关闭浏览器会话"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    # 创建爬虫实例
    scraper = AnalyticsScraper()
    
    try:
        # 获取小组赛数据
        group_stage_data = scraper.fetch_player_stats()
        scraper.export_to_csv(group_stage_data, "pgs8_m6.csv")
        
        # 获取决赛数据
        #finals_data = scraper.fetch_player_stats(round_type="finals")
        #scraper.export_to_csv(finals_data, "finals_stats.csv")
        
    finally:
        # 确保浏览器会话关闭
        scraper.close()

if __name__ == "__main__":
    main()