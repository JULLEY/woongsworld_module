import requests
import hashlib 
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import utils

def main():
    # 세션 생성 (TCP 연결 재사용)
    session = requests.Session()
    
    # User-Agent 설정
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    url = "https://www.gamemeca.com/news.php"

    # 게임메카 페이지수 query param   
    page_list=[f"p={i}" for i in range(1,2)]
    
    news_list=[]

    for page in page_list:
        request_url=url+"?"+page

        soup=utils.parse_news_page(session,request_url)
        news_items=soup.find_all('li')
        news_list.extend(news_items) 



    # DB 연결 설정 및 커서 생성        
    conn, curs = None, None

    try:
        #  conn, curs = utils.connect_db()

         recent_news_ids = utils.get_recent_news_ids(curs)


         with ThreadPoolExecutor(max_workers=10) as executor:

             for news in news_list:

                 a_tag=news.find('a',{'class':['link_thumb','static-thumbnail']})
                 title_div=news.find('div',{'class':['cont_thumb_h','cont_thumb']})  
                 desc_div=news.find('div',{'class':['desc_thumb_h','desc_thumb']})

                 if title_div and desc_div:

                     title_a_tag=title_div.find('a')

                     if title_a_tag:

                         title_text=title_a_tag.text.strip()  
                         link_url=urljoin(url,title_a_tag.get('href')) 

                     desc_text=desc_div.text.strip()  

                     hashed_title=hashlib.sha256(title_text.encode()).hexdigest()

                     # DB에 없는 기사만 Insert 처리
                     if hashed_title in recent_news_ids:
                         break
                     else:                 
                        orign_news=utils.parse_news_page(session,link_url)
                    
                        article=str(orign_news.find('div',{'class':'article'}))
                    
                        date=orign_news.find('span',{'class':'date'}).text

                        img_element_in_atag=a_tag.find("img")
                        
                        print(article)
                    
                        # if img_element_in_atag: 
                        #     img_url=img_element_in_atag["src"]
                        #     executor.submit(utils.download_image,session,img_url,hashed_title)

                            #DB Insert
                            # sql = "insert into news_pages(news_id, news_title, news_desc,\
                            #     url, news_content, created_date) value(%s,%s,%s,%s,%s,%s)"
                            
                            # try:
                            #     curs.execute(sql,(hashed_title,title_text,\
                            #                     desc_text,link_url,str(article),date))
                            # except Exception as e:
                            #     print(f"An error occurred while trying to insert data into the database: {str(e)}")
    finally:
        utils.close_db()        



if __name__ == "__main__":
    main()