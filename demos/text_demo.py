from RAI.AISystem import AISystem, Model
from RAI.redis import RaiRedis
from RAI.dataset import Dataset, Data, Feature
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from RAI.utils import df_to_RAI
from sklearn.model_selection import train_test_split
from datasets import load_dataset
import random
import numpy as np
import pandas as pd


def main():
    use_dashboard = True
    random.seed(0)
    np.random.seed(10)

    nltk.download("vader_lexicon")
    sentiment_model = SentimentIntensityAnalyzer()
    dataset = pd.DataFrame(load_dataset("rotten_tomatoes", split="train+test"))
    dataset['label'] = dataset['label'].astype('int64')
    dataset['text'] = dataset['text'].replace(-1, 0)
    new_dataset = dataset

    # TODO: Clarify running on numpy data across models
    def score_tweet(tweet: str) -> float:
        while isinstance(tweet, np.ndarray) or isinstance(tweet, list):
            tweet = tweet[0]
        return 0 if sentiment_model.polarity_scores(tweet)["compound"] <= 0 else 1

    meta, X, y, output = df_to_RAI(new_dataset, target_column="label", text_columns='text')
    xTrain, xTest, yTrain, yTest = train_test_split(X, y, random_state=1)
    output = Feature("Sentiment", "Numeric", "Sentiment Rating", categorical=True, values={
        0: "Negative", 1: "Positive"})

    preds = []
    for val in xTest:
        score = score_tweet(val[0])
        preds.append(score)

    model = Model(agent=sentiment_model, output_features=output, name="conv_net", predict_fun=score_tweet,
                  description="SentimentAnalysis", model_class="Bert")
    configuration = {"time_complexity": "polynomial"}
    dataset = Dataset({"train": Data(xTrain, yTrain), "test": Data(xTest, yTest)})
    ai = AISystem(name="Sentiment_Analysis_1", task='binary_classification', meta_database=meta, dataset=dataset, model=model)
    ai.initialize(user_config=configuration)

    ai.compute({"test": {"predict": preds}}, tag='initial_preds')

    if use_dashboard:
        r = RaiRedis(ai)
        r.connect()
        r.reset_redis(summarize_data=False)
        r.add_measurement()
        r.add_dataset()

    ai.display_metric_values()

    from RAI.Analysis import AnalysisManager
    analysis = AnalysisManager()
    print("available analysis: ", analysis.get_available_analysis(ai, "test"))
    # result = analysis.run_all(ai, "test", "Test run!")
    # result = analysis.run_analysis(ai, "test", "CleverUntargetedScore", "Testing")
    # for analysis in result:
    #    print("Analysis: " + analysis)
    #    print(result[analysis].to_string())


if __name__ == '__main__':
    main()