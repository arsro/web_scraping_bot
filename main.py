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
TARGET_URL   = 'https://192abc.com'
COLUMN_LIMIT = 20
ALL = 'all_target'


done_crawling = False
one_category_crawling = False
try:
	target_category_url = sys.argv[1]
	one_category_crawling = True
except IndexError:
	target_category_url = ALL

print(target_category_url)

# topページをクローリング
top_r = requests.get(TARGET_URL)
top_soup = BeautifulSoup(top_r.text, 'lxml')

# 大カテゴリ(large_category) -> 中カテゴリ(middle_category) -> 小カテゴリ(small_category)の順でクローリングします。
  
# 内容
output_bodies = []


# start crawling
# topページの下にある大カテゴリを取得します。
for categories in top_soup.find_all(class_='top-list__footer'):
	if done_crawling: break
		
	# Large categoryを取得
	for large_categories in categories.find_all(class_='footer-tags-list'):
		if done_crawling: break

		# 大カテゴリ
		print('Large_category : ' + re.sub(u'の関連カテゴリ', '', large_categories.find('h2').text))
		large_category = re.sub(u'の関連カテゴリ', '', large_categories.find('h2').text)
		
		# 大カテゴリ内の中カテゴリを取得します。
		for mid_categories in large_categories.find_all(class_='footer-tags-list__wrap'):
			if done_crawling: break

			for mid_category_link in mid_categories.select('ul > li > a'):
				
				# 中カテゴリ
				print("Middle_category : " + mid_category_link.text)
				middle_category = mid_category_link.text
				
				# 中カテゴリのリンク
				mid_target_url = TARGET_URL + mid_category_link.get('href')
				
				if (target_category_url != ALL) and (target_category_url != mid_target_url):
					break


				is_last = False
				page    = 0
				while not(is_last):
					page += 1
					sleep(1)
					print(mid_target_url + '/page/' + str(page))

					#　中カテゴリページをクローリングします。
					mid_r = requests.get(mid_target_url + '/page/' + str(page))
					mid_soap = BeautifulSoup(mid_r.text, 'lxml')
						
					# コンテンツがないページに行き付いたらクローリングを終了します。
					not_found_page = mid_soap.find('h1', class_='not-found__title')
					if not_found_page is not None:
						is_last = True
						continue

					# 中カテゴリに表示された各記事のリンクを取得します。
					for article_link in mid_soap.find_all(class_='list-article__link'):
						output_body = []

						
						# 記事へのリンク
						print('article link : ' + article_link.get('href'))
						output_body.append(article_link.get('href'))
						
						sleep(1)
						# 記事内をクローリングします。
						art_r = requests.get(article_link.get('href'))
						art_soap = BeautifulSoup(art_r.text, 'lxml')

						# 記事タイトル
						art_title = art_soap.find(class_='single-article__title entry-title')
						print('article title: ' + art_title.text)
						output_body.append(art_title.text)
						
						# 記事の大カテゴリ
						output_body.append(large_category)
						# 記事の中カテゴリ
						output_body.append(middle_category)
						# 記事の小カテゴリ
						small_category = art_soap.find(class_='ranking__title')
						print('Small_category : ' + re.sub(u'人気ランキング', '', small_category.text))
						output_body.append(re.sub(u'人気ランキング', '', small_category.text))

						# 監修者がいれば、監修者の専門と名前を取得
						supervisior_position = art_soap.find(class_='supervisor-profile__position')
						if supervisior_position is not None:
							print('supervisior position : ' + supervisior_position.text)
							output_body.append(supervisior_position.text)
						else:
							output_body.append('')
							
						supervisior_name = art_soap.find(class_='supervisor-profile__name')
						if supervisior_name is not None:
							print('supervisior name : ' + supervisior_name.text)
							output_body.append(supervisior_name.text)
						else:
							output_body.append('')
							
						# 記事内の関連リンク
						i = 0
						output_related_links = [''] * COLUMN_LIMIT
						for related_link in art_soap.find_all(class_='related__link'):
							output_related_links[i] = related_link.text
							print('related link : ' + related_link.text)
							i += 1
							if i >= COLUMN_LIMIT:
								print('OUT!')
								break

						for link in output_related_links:
							output_body.append(link)
							pass

						# 参考記事
						i = 0
						output_reference_links = [''] * (COLUMN_LIMIT-5)
						for reference_link in art_soap.find_all(class_='reference__link'):
							output_reference_links[i] = reference_link.text
							print('reference link : ' + reference_link.text)
							# output_reference_links.append(reference_link.text)
							i += 1
							if i >= COLUMN_LIMIT-5:
								print('OUT!')
								break

						for link in output_reference_links:
							output_body.append(link)
							pass
						
						# 関連キーワード
						i = 0
						output_related_kws = [''] * COLUMN_LIMIT
						related_kws = art_soap.find(class_="related-tags")
						for related_kw in related_kws.select('ul > li > a'):
							output_related_kws[i] = related_kw.text
							print('related kw : ' + related_kw.text)
							i += 1
							if i >= COLUMN_LIMIT:
								print('OUT!')
								break

						print(output_related_kws)

						for kw in output_related_kws:
							output_body.append(kw)

						output_bodies.append(output_body)
					
					if one_category_crawling:
						done_crawling = True

columns=[
'記事URL', '記事タイトル', '大カテゴリ', '中カテゴリ' , '小カテゴリ', '記事監修 専門','記事監修 名前',
'関連リンク'     , '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'参考記事'       , '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'関連キーワード' , '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
]
now = datetime.now().strftime('%y%m%d')

pandas.DataFrame(output_bodies, columns=columns).to_csv("192abccom_"+now+".csv",encoding='utf-8')
		
print('end crawling!')
