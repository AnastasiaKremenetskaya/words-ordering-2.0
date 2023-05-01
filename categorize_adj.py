# Import libraries
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.svm import SVC


class CategorizeADJ:
    def __init__(self):
        # Loading GloVe
        print("Initializing GloVe embedding")
        self.embed_dict = {}
        # with open('./word2vec/adjective_embeddings.txt', 'r') as f:
        with open('/Users/anterekhova/PycharmProjects/words-ordering/dataset/glove.6B.200d.txt', 'r') as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], 'float32')
                self.embed_dict[word] = vector
        print("Initialized GloVe embedding")

        # Loading dataset
        print("Initializing ADJ class data")
        self.data = pd.read_csv(
            '/Users/anterekhova/PycharmProjects/words-ordering/dataset/accuracy_test.csv')  # pd.read_csv('/Users/anterekhova/PycharmProjects/eyes/ordering_adjectives/dataset/adj_category.csv')
        print("Initialized ADJ class data")

        # Loading dataset for KNN
        print("Initializing KNN")
        self.le = preprocessing.LabelEncoder()
        self.le.fit(self.data.Class.unique().tolist())

        self.y_train = self.le.transform(
            self.data.Class.values.tolist())  # представляем классы в виде нумерованного списка
        words = self.data.Word.values.tolist()
        self.x_train = np.array([self.embed_dict[word] for word in words])

        self.neigh = SVC()
        # self.neigh = KNeighborsClassifier(n_neighbors=3)
        # для обучения укладываем тренировочные данные, чтобы knn мог
        # после предсказания выбрать класс, наиболее схожий со словами из тренировочного датасета
        self.neigh.fit(self.x_train, self.y_train)

        print("Initialized KNN")

        data = pd.read_csv('/Users/anterekhova/PycharmProjects/words-ordering/dataset/accuracy_test.csv')
        self.x_test = np.array([self.embed_dict[word] for word in data.Word.values.tolist()])
        self.y_test = self.le.transform(list(data.Class.values.tolist()))

    def infer(self, word):
        # если нашли в словаре категорий
        idx = self.data[self.data['Word'] == word.lower()].Class.tolist()
        if len(idx) == 0:
            if 'shaped' in word:
                return 'Shape'
            if '-type' in word:
                return 'Type'
            if word.endswith('ing'):
                return 'Purpose'
            try:
                # берем векторное представление прилагательного
                embed_vector = self.embed_dict[word]
                x_test = embed_vector.reshape(1, -1)
                # определяем ближайший по схожести класс
                x_pred = self.neigh.predict(x_test)
                a = self.le.inverse_transform(x_pred).tolist()
                return a[0]
            except:
                return 'Origin'
        else:
            return idx[0]


if __name__ == "__main__":
    categorizer = CategorizeADJ()
    print(categorizer.infer('bread-like'))
    print(categorizer.infer('wool'))
