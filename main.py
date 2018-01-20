# coding: UTF-8
import codecs
import pandas
import re
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

# エンコードの設定
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

# 定数
# 対象のURL
TARGET_URL   = 'https://mamari.jp'
SITE_MAP_URL = 'https://mamari.jp/map'
COLUMN_LIMIT = 15
ALL = 'all_target'


done_crawling = False
one_category_crawling = False
try:
	target_category_url = sys.argv[1]
	one_category_crawling = True
	
	# print target_category_url + u'をクローリングします'
except IndexError:
	target_category_url = ALL

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'}
# topページをクローリング
top_r = requests.get(SITE_MAP_URL, headers=headers)
top_soup = BeautifulSoup(top_r.text, 'lxml')

  
# 内容
output_bodies = []

# start crawling
# topページの下にある大カテゴリを取得します。
category_list = top_soup.find(class_='content-wrap')
for categories in category_list.find_all(class_='column'):
	if done_crawling: break
	
	for category_link in categories.select('ul > li > a'):
		# print category_link
		
        # とりあえず中カテゴリのリンクを取得
		mid_target_url = TARGET_URL + category_link.get('href')
		# print mid_target_url
        # 指定のURLでないときはスキップ
		if (target_category_url != ALL) and (target_category_url != mid_target_url):
			continue
        # endif
		        
        # 中カテゴリからページングするので、ページングに必要な初期値を設定する
		is_last = False
		page = 0
		while not(is_last):
			page+=1
			
			# print "page: " + str(page)
			# print "is last: " + str(is_last)
			sleep(5)
            # 中カテゴリのクローリング
			mid_r = requests.get(mid_target_url + '/?page=' + str(page), headers=headers)
			mid_soap = BeautifulSoup(mid_r.text, 'lxml')
			
			# コンテンツがないページに行き付いたらクローリングを終了する
			not_found_page = mid_soap.find('p', class_='p-error__content__title')
			if not_found_page is not None:
				is_last = True
				# print u'このページに記事はありませんでした。このカテゴリでのクローリングを終了します。'
				continue
			# endif
			
			# 関連カテゴリ
			rel_category = mid_soap.find('h3', class_='subarea-section-headline').text
			rel_category = re.sub(u'の人気記事', '', rel_category)
			
			# 中カテゴリに表示された各記事のリンクを取得します。
			for article_title in mid_soap.find_all(class_='article-title'):
				output_body = []
				
				article_link = TARGET_URL + article_title.find('a').get('href')
				# 記事へのリンク
				# print u'記事へのリンク'
				# print article_link
				output_body.append(article_link)

				sleep(5)
				# 記事内をクローリングします。
				art_r = requests.get(article_link, headers=headers)
				art_soap = BeautifulSoup(art_r.text, 'lxml')

				# 記事タイトル
				# print u'記事タイトル'
				art_title = art_soap.find(class_='article-top-title')
				# print art_title.text.strip()
				output_body.append(art_title.text.strip())

				# print u'関連カテゴリ'
				# print rel_category
				output_body.append(rel_category)

				breadcrumbs = art_soap.find(class_='c-breadcrumb clearfix')
				j = 0
				output_cateroies = ['', '', '', '']
				# 記事の大カテゴリ→記事の中カテゴリ→記事の小1カテゴリ→記事の小2カテゴリ
				for i, breadcrumb in enumerate(breadcrumbs.find_all(class_='c-breadcrumb__item')):
                    # 小カテゴリ2以上は取得しない
					if i >= 5: break
					if breadcrumb.find('span') is None: continue
					if breadcrumb.find('span').text == 'トップ': continue
					
					# print u'カテゴリ'
					# print breadcrumb.find('span').text
					output_cateroies[j] = breadcrumb.find('span').text
					j += 1
					if j >= 4: break
				# endfor
				
				for category in output_cateroies:
					output_body.append(category)
					pass

				# 監修者がいれば、監修者の専門と名前を取得
				supervisior = art_soap.find(class_='p-article-supervisor__content clearfix')
				if supervisior is not None:
					# print u'監修者　専門'
					# print supervisior.find('p', class_='p-article-supervisor__content__inner__job-title').text.strip()
					# print u'監修者　名前'
					# print supervisior.find('a', class_='p-article-supervisor__content__inner__name').text.strip()
					output_body.append(supervisior.find('p', class_='p-article-supervisor__content__inner__job-title').text.strip())
					output_body.append(supervisior.find('a', class_='p-article-supervisor__content__inner__name').text.strip())
				else:
					# print u'監修者いません'
					output_body.append('')
					output_body.append('')
                # endif
				
				
				# 記事内の関連リンク
				# print u'記事内の関連リンク'
				i = 0
				output_related_links = [''] * COLUMN_LIMIT
				for related_link in art_soap.find_all(class_='article-content__introduction-link__media--space-none article-content__introduction-link__media__title'):
					# print related_link.text.strip()
					output_related_links[i] = related_link.text.strip()
					i += 1
					if i >= COLUMN_LIMIT: break
                # endfor

				for link in output_related_links:
					output_body.append(link)
					pass
				# endfor

				# 参考記事
				# print u'参考記事リンク'
				i = 0
				output_reference_links = [''] * (COLUMN_LIMIT-5)
				for reference_link in art_soap.find_all(class_='p-source-block__list__item__title'):
					# print reference_link.text.strip()
					output_reference_links[i] = reference_link.text.strip()
					i += 1
					if i >= COLUMN_LIMIT-5: break
				# endfor
				
				for link in output_reference_links:
					output_body.append(link)
					pass
				# endfor


				# 関連キーワード
				# print u'関連キーワード'
				i = 0
				output_related_kws = [''] * COLUMN_LIMIT
				if art_soap.find(class_="article-guide"):
					related_kw = art_soap.find(class_="article-guide").find('p').text
					if related_kw:
						related_kw = re.sub(u'についてもっと詳しく知る', '', related_kw)
						kws = related_kw.split("「")
						if kws:
							for kw in kws:
								kw = re.sub(u'」', '', kw)
								# print kw
								if kw == '': continue

								output_related_kws[i] = kw.strip()
								i += 1
								if i >= COLUMN_LIMIT: break
								
		                    # endfor
		                # endif
						pass
		            # endif
				# endif
				
				for kw in output_related_kws:
					output_body.append(kw)
                # endfor

                # マージ
				output_bodies.append(output_body)

                # もし1つのカテゴリのみのクローリングだったら、終了
				if one_category_crawling: done_crawling = True

            # endfor
        # endwhile
    #endif
#endfor
	

columns=[
'記事URL', '記事タイトル', '関連カテゴリ', '大カテゴリ', '中カテゴリ' , '小カテゴリ1', '小カテゴリ2', '記事監修 専門','記事監修 名前',
'関連リンク'     , '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'参考記事'       , '', '', '', '', '', '', '', '', '',
'関連キーワード' , '', '', '', '', '', '', '', '', '', '', '', '', '', ''
]
now = datetime.now().strftime('%y%m%d')

pandas.DataFrame(output_bodies, columns=columns).to_csv("mamari_"+now+".csv",encoding='utf-8')
