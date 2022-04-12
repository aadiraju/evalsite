
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer


class Recommendations:

    def __init__(self, user_id, df, ratings_df):
        self.df = df
        self.mapping = pd.Series(self.df.index, index=self.df['video_id'])
        ratings_df['video'] = ratings_df.apply(
            lambda x: self.mapping[x['video_id']], axis=1)
        self.ratings_df = ratings_df.pivot(
            index='user_id', columns='video', values='rating')
        self.user_id = user_id

    def text_similarity_matrix(self):
        # TF-IDF Vectorizer to convert the text data into a sparse numeric matrix ready to compare
        tfidf = TfidfVectorizer(stop_words='english')

        description_matrix = tfidf.fit_transform(self.df['description'])
        title_matrix = tfidf.fit_transform(self.df['title'])

        # Cosine Similarity matrix between each video
        desc_simmat = cosine_similarity(description_matrix)
        title_simmat = cosine_similarity(title_matrix)

        return np.add(title_simmat * 0.5, desc_simmat * 0.5)

    def numeric_similarity_matrix(self):
        final_df = self.df[['vls', 'duration']].copy()

        # pairwise distances
        dists = euclidean_distances(final_df, final_df)

        # Map the pairwise distances onto a range of [0,1]
        scaling_factor = 1/np.ptp(dists)

        # Take the inverse of the distances so that closer distances have higher similarities
        numeric_sim = 1 - (scaling_factor * dists)

        return numeric_sim

    def get_weighted_simil_matrix(self, w1, w2):
        num_simmat = self.numeric_similarity_matrix()
        text_simmat = self.text_similarity_matrix()
        return np.add(w1*num_simmat, w2*text_simmat)

    def recommend_content_based(self, video_id, w1, w2):
        video_idx = self.mapping[video_id]

        # compute weighted cosine similarity
        simmat = self.get_weighted_simil_matrix(w1, w2)

        simscore = list(enumerate(simmat[video_idx]))

        # Get similarity score in descending order and Skip the first video since that is the seed
        # Need to use key function because it is a list of tuples in the format (df_index, similarity_score)
        simscore = sorted(simscore, key=lambda x: x[1], reverse=True)[1:]

        simscore = simscore[:5]

        # Get dataframe indices in order
        video_idxs = [i[0] for i in simscore]

        return (self.df['video_id'].iloc[video_idxs].copy())

    @staticmethod
    def get_mean_or_none(values):
        mean = values[values != 0].mean()
        return mean if not pd.isna(mean) else 0

    def predict_rating_helper(self, video_id, user_id, simil, ratings_df):
        # similarity scores between user_id and other users
        simscores = simil[user_id]
        # ratings by other users for this video_id
        other_ratings = ratings_df.iloc[:, video_id]

        # mean for current user
        user_mean = self.get_mean_or_none(ratings_df.loc[user_id])

        predicted_rating = 0
        for i in simil:
            if i == user_id:
                continue
            r_i_k = other_ratings[i] if not pd.isna(other_ratings[i]) else 0
            if r_i_k == 0:
                continue
            mean_i = self.get_mean_or_none(ratings_df.loc[i])
            predicted_rating += simscores[i] * (r_i_k - mean_i)

        final_rating = predicted_rating + user_mean
        if final_rating < 1.0:
            return 1
        elif final_rating > 5.0:
            return 5
        else:
            return round(final_rating)

    def predict_rating(self, video_id, user_id):
        ratings_df = self.ratings_df
        test_df = ratings_df.copy()
        test_df = test_df.fillna(0)
        user_simil = cosine_similarity(test_df, test_df)
        simil = pd.DataFrame(
            user_simil, index=test_df.index, columns=test_df.index)
        return self.predict_rating_helper(video_id, user_id, simil, test_df)

    def get_recommendations(self, seed_video, alpha=0.5):
        content_recs = self.recommend_content_based(seed_video, 0.3, 0.7)  # As determined by content-based benchmarking
        collab_recs = {'video_id': [], 'ratings': []}
        for video_id in content_recs:
            collab_recs['video_id'].append(video_id)
            collab_recs['ratings'].append(self.predict_rating(
                self.mapping[video_id], self.user_id))

        content_recs = content_recs.reset_index()
        content_recs['ranking'] = content_recs.index + 1
        content_recs['ranking'] = content_recs['ranking'] * alpha

        collab_recs_df = pd.DataFrame.from_dict(collab_recs)
        collab_recs_df = collab_recs_df.sort_values(
            by=['ratings'], ascending=False)
        collab_recs_df = collab_recs_df.reset_index()
        collab_recs_df['ranking'] = collab_recs_df.index + 1
        collab_recs_df['ranking'] = collab_recs_df['ranking'] * (1 - alpha)

        recs = pd.merge(content_recs, collab_recs_df, how='inner', on=[
                        'video_id'], suffixes=['1', '2'])

        recs['ranking'] = recs['ranking1'] + recs['ranking2']
        recs = recs[['video_id', 'ranking']]

        return recs.sort_values(by=['ranking']).to_dict('records')
