# crime_in_Seoul_datat
‣ 교재 [파이썬으로 데이터 주무르기](http://www.yes24.com/Product/Goods/57670268)를 참고했습니다.

---

## ⭐️서울시 구별 5대 범죄현황 분석(ver2015)⭐️

### ✅ 데이터
#### 1. 데이터 가져오기
| 대상 데이터 | 출처 | 내용 
| :- | - | :-: | 
| 서울시 범죄 현황 데이터 | [서울 열린 데이터 광장](https://data.seoul.go.kr/dataList/datasetList.do)  | 서울시 경찰서별 검거율, 서울특별시 관서별 5대 범죄 현황
| 서울시 CCTV 현황 데이터 | [서울 열린 데이터 광장](https://data.seoul.go.kr/dataList/datasetList.do)  | 구별 인구수, 구별 CCTV 현황
| 경찰서 위치 데이터 | [구글 클라우드 플랫폼](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com?project=quixotic-strand-305510) | 서울시 경찰서별 주소, 서울시 지도

+ 2016년 이후 범죄 현황 데이터는 구별 경찰서의 정보를 포함하므로 2015년 데이터를 활용했습니다. (지리 정보 데이터 활용 익히기)

#### 2. 데이터 가공하기
|라이브러리 | 용도
| :- | - 
| Numpy, Pandas, Sklearn| 데이터 병합, 전처리, 정리
| Matplotlib, Seaborn | 데이터 시각화 
| Wordcloud | 워드 클라우드(Word Cloud) 구현

### ✅ 결과물
1. Jupyter Notebook
2. 웹 페이지 생성
|내용 | 구현 방식 
| :- | - 
| 웹 UI, 디자인 | Bootstrap 
| 구현 | html, css 
| 배포(진행 중) | Netflify 웹 호스팅 서비스

### ✅ 소스 코드
[깃허브 레포지토리](https://github.com/HyunJin0505/crime_in_Seoul_data)




