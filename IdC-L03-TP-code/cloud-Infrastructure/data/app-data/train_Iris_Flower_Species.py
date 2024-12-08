import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier # neural network
from keras.models import Sequential 
from keras.layers import Dense,Activation,Dropout 
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import joblib
import gzip



# my personal reusable function for detecting missing data
def missing_value_describe(data):
    # check missing values in training data
    missing_value_stats = (data.isnull().sum() / len(data)*100)
    missing_value_col_count = sum(missing_value_stats > 0)
    missing_value_stats = missing_value_stats.sort_values(ascending=False)[:missing_value_col_count]
    print("Number of columns with missing values:", missing_value_col_count)
    if missing_value_col_count != 0:
        # print out column names with missing value percentage
        print("\nMissing percentage (desceding):")
        print(missing_value_stats)
    else:
        print("No misisng data!!!")






# load the iris dataset
iris_data = pd.read_csv('data/Iris.csv')

missing_value_describe(iris_data)

iris_data = iris_data.drop(['Id'], axis=1)
iris_data.columns

# dimension
print("the dimension:", iris_data.shape)

# class distribution
print(iris_data.groupby('Species').size())





# we will split data to 80% training data and 20% testing data with random seed of 10
X = iris_data.drop(['Species'], axis=1)
Y = iris_data['Species']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=7)

print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("Y_train.shape:", X_train.shape)
print("Y_test.shape:", Y_test.shape)


# models
models = []

# linear models
models.append(('LR', LogisticRegression(solver='liblinear', multi_class="auto"))) #regularized logistic regression
models.append(('LDA', LinearDiscriminantAnalysis()))                              #Linear Discriminant Analysis

# nonlinear models
models.append(('DT', DecisionTreeClassifier()))  #decision tree classifier
models.append(('KNN', KNeighborsClassifier()))   #k-nearest neighbors
models.append(('GNB', GaussianNB()))      	 #Gaussian Naive Bayes
models.append(('SVC', SVC(gamma="auto"))) 	 #Support Vector Classification

models.append(('MLP', MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(3, 3), random_state=1))) #multi-layer perceptron (MLP) algorithm


# evaluate each model in turn
print("Model Accuracy:")
names = []
accuracy = []
for name, model in models:
    # 10 fold cross validation to evalue model
    kfold = KFold(n_splits=10, shuffle=True)
    cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='accuracy')
    
    # display the cross validation results of the current model
    names.append(name)
    accuracy.append(cv_results)
    msg = "%s: accuracy=%f std=(%f)" % (name, cv_results.mean(), cv_results.std())
    print(msg)


# reusable function to test our model
def test_model(name, model):
    model.fit(X_train, Y_train) # train the whole training set
    
    # Export model
    joblib.dump(model, gzip.open('model/iris-' + name + '.dat.gz', "wb"))
    
    
    predictions = model.predict(X_test) # predict on test set
    
    # output model testing results
    print("Accuracy:", accuracy_score(Y_test, predictions))
    print("Confusion Matrix:")
    print(confusion_matrix(Y_test, predictions))
    print("Classification Report:")
    print(classification_report(Y_test, predictions))
    
    

# predict values with our test set
for name, model in models:
    print("----------------")
    print("Testing", name)
    test_model(name, model)
    


