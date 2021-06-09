#!/usr/bin/env python
# coding: utf-8

# # 데이터 정리하기

# ## 1. 5대 범죄 데이터 확인, 경찰서 위치 정보 저장

# 1. 다운받은 서울시 범죄현황 데이터를 불러와 확인
# **Notice** 지도 데이터로 위치 정보 알기, pivot_table 등 응용을 위해서 2015년 데이터 활용(2019데이터는 이미 구별로 정보 나뉘어 있음)

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


crime_anal_police = pd.read_csv('data/02. crime_in_Seoul.csv', thousands=',',encoding="euc-kr" )
crime_anal_police.head()


# 2. Googl Maps Geocoding API로 관서별 경도,위도 정보 가져오기
# 
# 
# 다운받은 데이터가 관서별로 정리되어 있음 -> 구별로 정보를 확인하기 위해서 데이터 받아오기

# In[3]:


import googlemaps


# In[4]:


gmaps_key = "*****************"
gmaps = googlemaps.Client(key=gmaps_key)


# In[5]:


gmaps.geocode('서울중부경찰서', language='ko')


# + data에 관서 이름이 '중부서'형식으로 되어있는걸 google maps의 양식('서울중부경찰서')으로 수정

# In[6]:


station_name = []
for name in crime_anal_police['관서명']:
    station_name.append('서울'+str(name[:-1])+'경찰서')
station_name


# + 각 경찰서별 주소 얻기
#   + 위도, 경도 데이터는 이후 지도 시각화에 필요하므로 미리 저장하기

# In[7]:


station_address = []
station_lat = []
station_lng = []

for name in station_name:
    tmp = gmaps.geocode(name, language="ko")
    station_address.append(tmp[0].get("formatted_address"))
    tmp_loc = tmp[0].get("geometry")
    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])
    print(name+'-->'+tmp[0].get("formatted_address"))


# In[8]:


station_address


# In[9]:


station_lat


# In[10]:


station_lng


# + 관서명에서 각 구를 파악하고 컬럼 추가하기

# In[11]:


gu_name = []
for name in station_address:
    tmp = name.split() #스페이스로 구분하여 두 번쨰 단어를 가르킴(구 명)
    tmp_gu = [gu for gu in tmp if gu[-1] == "구"][0]
    gu_name.append(tmp_gu)
    
crime_anal_police['구별'] = gu_name
crime_anal_police.head()


# + 금천서는 관악구에 있으므로 '구별'명을 금천구로 변경

# In[13]:


crime_anal_police.loc[crime_anal_police['관서명']=='금천서', ['구별']] = '금천구'
crime_anal_police[crime_anal_police['관서명']=='금천서']


# + 구 이름을 포함한 data를 csv파일로 저장(저장 안 하면 실행마다 처음부터 데이터 받아와야함)

# In[14]:


crime_anal_police.to_csv('data/02. crime_in_Seoul_include_gu_name.csv', sep=',', encoding="utf-8")


# In[15]:


crime_anal_police.head()


# ## 2. 범죄 데이터를 구별로 정리하기 with Pivot Table

# In[16]:


import pandas as pd
import numpy as np


# In[17]:


crime_anal_raw = pd.read_csv('data/02. crime_in_Seoul_include_gu_name.csv', encoding='utf-8')
crime_anal_raw.head()


# + pivot_table로 관서별 데이터를 구별로 바꾸기
#   + aggfunc=np.sum 을 통해 구별 데이터의 총합을 구하기

# In[18]:


crime_anal = pd.read_csv('data/02. crime_in_Seoul_include_gu_name.csv', encoding='utf-8', index_col=0)
crime_anal = pd.pivot_table(crime_anal_raw, index="구별", aggfunc=np.sum)
crime_anal.head()


# + 검거율을 계산하고, 검거 건수는 지우기

# In[21]:


crime_anal['강간검거율'] = crime_anal['강간 검거']/crime_anal['강간 발생']*100
crime_anal['강도검거율'] = crime_anal['강도 검거']/crime_anal['강도 발생']*100
crime_anal['살인검거율'] = crime_anal['살인 검거']/crime_anal['살인 발생']*100
crime_anal['절도검거율'] = crime_anal['절도 검거']/crime_anal['절도 발생']*100
crime_anal['폭력검거율'] = crime_anal['폭력 검거']/crime_anal['폭력 발생']*100

del crime_anal['강간 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']

crime_anal.head()


# + 전년도 검거 건수 영향으로 검거율이 100%넘는 경우, 100으로 통일해줌
# 
#         .loc[인덱스, 컬럼]

# In[23]:


con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

for column in con_list:
    crime_anal.loc[crime_anal[column] >= 100, column] = 100
    
crime_anal.head()


# + 컬럼명에서 '발생' 지우기
#         rename함수
#         기존 df에 값을 덮어쓰려면 inplace=True 옵션 넣기

# In[22]:


crime_anal.rename(columns= {'강간 발생':'강간',
                            '강도 발생':'강도',
                            '살인 발생':'살인',
                            '절도 발생':'절도',
                            '폭력 발생':'폭력'}, inplace=True)
crime_anal.head()


# ## 3. 데이터 표현 위해 다듬기

# + sklearn패키지의 preprocessing 기능을 사용해서 값의 자릿수 맞추기
#   + 각 항목의 최댓값을 1로 두고 비율에 따라 소숫점아래 6자리 수로 정규화->이후 비교 수월 목적

# In[24]:


from sklearn import preprocessing

col = ['강간', '강도', '살인', '절도', '폭력']

x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()

x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns = col, index = crime_anal.index)

col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2]
crime_anal_norm.head()


# + CCTV_result.csv파일을 불러와서 구별 인구수 받아오기
#   + CCTV데이터에 포함된 구별 인구수 데이터 활용

# In[28]:


result_CCTV = pd.read_csv('data/01. CCTV_result.csv', encoding='utf-8', index_col='구별')
crime_anal_norm[['인구수']] = result_CCTV[['인구수']]
crime_anal_norm.head()


# + 구별 범죄 발생 건수의 합, 검거율의 합 구하기
# 
# 
# + np.sum의          
#   + axis=1은 y축 기준의 합계를 의미한다
#   + axis=0은 x축 기준의 합계를 의미한다
#   + axis=None은 대상 데이터의 모든 요소의 합계를 의미한다

# In[29]:


col1 = ['강간','강도','살인','절도','폭력']
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col1], axis=1)
crime_anal_norm.head()


# In[30]:


col = ['강간검거율','강도검거율','살인검거율','절도검거율','폭력검거율']
crime_anal_norm['검거'] = np.sum(crime_anal_norm[col], axis=1)
crime_anal_norm.head()


# ## 4. seaborn으로 데이터 시각화하기

# **seaborn**
# matplotlib기반으로 동작하는 시각화 라이브러리 
# pairplot과 같은 탐색적 분석을 위한 기능을 제공함

# + matplotlib가 한글 폰트를 제공하지 않으므로 이를 해결하는 코드 필요

# In[31]:


pip install seaborn


# In[39]:


pip install platform


# In[35]:


import matplotlib.pyplot as plt
import seaborn as sns

get_ipython().run_line_magic('matplotlib', 'inline')

import platform

path = "c:/Windows/Fonts/malgun.ttf"
from matplotlib import font_manager, rc
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~')


# In[38]:


crime_anal_norm


# + **sns.pairplot**메소드로 '강도','살인','폭력' 데이터의 관계 확인하기
#   + crime_anal_norm 데이터프레임 객체를 넘겨 그래프로 그리고 싶은 데이터 정하기
#   + 'vars'파라미터에 그리고 싶은 데이터 칼럼 이름 넘기기
#   + 'kind'파라미터를 통해 그래프 종류 선택하기. 'scatter','kde','hair','reg'네 종류 지원
#   + 'hue'파라미터에 칼럼 이름 넘겨서 그 칼럼의 데이터를 기준으로 그래프의 색을 다르게 보여줌
#     + (hue 피라미터를 사용하지 않았지만 범주형 데이터가 포함된 시각화에서 유용하게 사용가능)
# 
# 

# In[39]:


sns.pairplot(crime_anal_norm, vars=['강도','살인','폭력'],kind='reg', size=3)
plt.show()


# + 검거율 비교하기
#  + '검거'칼럼 값(검거율의 함)을 최대값으로 나누어 정규화해주기
#  + 정규화한 '검거'칼럼 값을 기준으로 정렬하기

# In[40]:


crime_anal_norm['검거']=crime_anal_norm['검거']/crime_anal_norm['검거'].max()
crime_anal_norm_sort = crime_anal_norm.sort_values(by='검거', ascending=False)
crime_anal_norm_sort.head()


# + **Seaborn라이브러리 heatmap메서드로 시각화**
# 
# 
# **(1)검거율 시각화**
# + crime_anal_norm_sort[cols]를 넘긴-> 히트맵으로 시각화하려는 데이터프레임 정하기
# + annot파라미터를 True로 설정-> 범죄 검거 비율 값을 히트맵의 각 셀 위에 주석으로 달아준다

# 시각화 결과
#   + 범죄 검거율 Best3 : 도봉구, 금천구, 강서구
#   + 범죄 검거율 Worst3 : 중구, 동작구, 구로구

# In[41]:


cols = ['강간검거율','강도검거율','살인검거율','절도검거율','폭력검거율']
plt.figure(figsize=(10,10))
sns.heatmap(crime_anal_norm_sort[cols], annot=True, fmt='f', 
                    linewidths=.5, cmap='RdPu')
plt.title('범죄 검거 비율 (정규화된 검거의 합으로 정렬)')
plt.show()


# **(2)범죄 발생량 시각화**
# + 보기에 편하게 만들기 위해서 범죄 칼럼 값을 5로 나눔 -> 0~1 사이 값을 갖게 하기

# 시각화 결과 
# + 범죄 발생 빈도 Top3: 강남구, 영등포구, 송파구
# + 범죄 발생 빈도 Bottom3: 도봉구, 서대문구, 금천구

# In[42]:


target_col = ['강간', '강도', '살인', '절도', '폭력', '범죄']

crime_anal_norm['범죄'] = crime_anal_norm['범죄'] / 5
crime_anal_norm_sort = crime_anal_norm.sort_values(by='범죄', ascending=False)

plt.figure(figsize = (10,10))
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', linewidths=.5,
                       cmap='RdPu')
plt.title('범죄비율 (정규화된 발생 건수로 정렬)')
plt.show()


# In[43]:


crime_anal_norm.to_csv('data/02. crime_in_Seoul_final.csv', sep=',', 
                       encoding='utf-8')


# ### Folium으로 지도 시각화하기

# In[47]:


pip install folium


# In[47]:


import folium


# + **경찰서별 검거현황과 구별 범죄발생 현황 시각화**
#   + 미리 저장해 놓은 구별 경찰서의 위치 정보 사용하기

# In[48]:


crime_anal_raw['lat'] = station_lat
crime_anal_raw['lng'] = station_lng

col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
tmp = crime_anal_raw[col] / crime_anal_raw[col].max()
    
crime_anal_raw['검거'] = np.sum(tmp, axis=1)

crime_anal_raw.head()


# ( 서울 지도 데이터 불러오기. 출처: https://pinkwink.kr/971)

# In[49]:


import json
geo_path = 'data/02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))


# In[50]:


map = folium.Map(location=[37.5502, 126.982], zoom_start=11, 
                 tiles='Stamen Toner')

map.choropleth(geo_data = geo_str,
               data = crime_anal_norm['범죄'],
               columns = [crime_anal_norm.index, crime_anal_norm['범죄']],
               fill_color = 'PuRd', #PuRd, YlGnBu
               key_on = 'feature.id')
map


# In[51]:


map.save('crime_total.html')


# + 각 경찰서의 위치를 지도로 시각화하기

# In[52]:


map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

for n in crime_anal_raw.index:
    folium.Marker([crime_anal_raw['lat'][n], 
                   crime_anal_raw['lng'][n]]).add_to(map)
    
map


# In[53]:


map.save('police.html')


# + 

# In[54]:


map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

for n in crime_anal_raw.index:
    folium.CircleMarker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]], 
                        radius = crime_anal_raw['검거'][n]*10, 
                        color='#3186cc', fill_color='#3186cc', fill=True).add_to(map)
    
map


# In[57]:


map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data = geo_str,
               data = crime_anal_norm['범죄'],
               columns = [crime_anal_norm.index, crime_anal_norm['범죄']],
               fill_color = 'PuRd', #PuRd, YlGnBu
               key_on = 'feature.id')

for n in crime_anal_raw.index:
    folium.CircleMarker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]], 
                        radius = crime_anal_raw['검거'][n]*10, 
                        color='#3186cc', fill_color='#3186cc', fill=True).add_to(map)
    
map


# In[56]:


final_map.save('final.html')


# ## 데이터로 워드클라우드 구현하기

# (데이터가 숫자로 표현되어 있어서 빈도를 워드 클라우드로 구현하는 것 불가능. 가능한 방법 모색중)

# In[93]:


pip install wordcloud


# In[99]:


import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud


# In[186]:


f = open("/Users/hyunjinlee/Downloads/report.txt")
line = f.readline()
print(line)
f.close()


# In[187]:


## LOAD TEXTS
text = line

## CREATE WORDCLOUD
wc = WordCloud(
    font_path='/Users/hyunjinlee/Library/Fonts/NanumSquare_acB.ttf',
    background_color='white'
)
wc.generate(text)

# SHOW WORDCLOUD
plt.figure(figsize=(20,20))

plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

