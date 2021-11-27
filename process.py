from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import json

class ContentProcessor:
    @staticmethod
    def split_content():
        kkma = Kkma()    

        with open('job_detail_list.json', 'r',encoding='UTF-8') as f:
            json_data = json.load(f)
        
        for data in json_data:
            sample = kkma.nouns(data['job'] + ' ' + data['contents'] + ' ' + data['name'])
            data['nouns'] = sample
        
        with open('konl_job_detail0.json', 'w', encoding='utf-8') as make_file:
                json.dump(json_data, make_file,ensure_ascii=False, indent="\t")

class SimilarityAnalyzer:
    @staticmethod
    def export_csv(list, name):
        tfidf_vectorizer = TfidfVectorizer(min_df=1,analyzer= 'word')
        tfidf_matrix = tfidf_vectorizer.fit_transform(list)

        df1 = pd.DataFrame(tfidf_matrix)
        df1.to_csv('tfidf_job_' + name + '.csv')

        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        df2 = pd.DataFrame(cosine_sim)
        df2.to_csv('cossim_job_' + name + '.csv')

    @staticmethod
    def analyze():
        with open('konl_job_detail0.json', 'r',encoding='UTF-8') as f:
            json_data = json.load(f)
        
        nouns_list = []
        addresses_list = []
        for detail in json_data:
            nouns = detail['nouns']
            sentance = ''
            for noun in nouns:
                sentance += noun + ' '
            nouns_list.append(sentance)

            addresses_list.append(detail['address'])
        
        SimilarityAnalyzer.export_csv(nouns_list, 'detail0')
        SimilarityAnalyzer.export_csv(addresses_list, 'address')

class Recommender:
    @staticmethod
    def recommend(job_index):
        with open('job_detail_list.json', 'r',encoding='UTF-8') as f:
            json_data = json.load(f)

        cossim_detail_matrix= pd.read_csv('cossim_job_detail0.csv')
        cossim_address_matrix= pd.read_csv('cossim_job_address.csv')
        
        sim_detail_scores = list(enumerate(cossim_detail_matrix.iloc[job_index]))
        sim_address_scores = list(enumerate(cossim_address_matrix.iloc[job_index]))

        sum_scores = []
        for score in sim_detail_scores:
            # 단어유사도 > 위치 가중치
            new_score = (score[1] * 1.5) + sim_address_scores[score[0]][1]
            sum_scores.append(new_score)

        sim_scores = list(enumerate(sum_scores))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:11]

        index_list = [i[0] for i in sim_scores]
        print(json_data[job_index])
        print([json_data[i]['job'] for i in index_list])
        

if __name__ == "__main__":
    ContentProcessor.split_content()
    SimilarityAnalyzer.analyze()
    Recommender.recommend(2)