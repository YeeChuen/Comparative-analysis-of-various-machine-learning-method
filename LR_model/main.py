from logistic_regression import LogisticRegression
from helper import parseData, splitData, normalize, ensemble_wrapper, poly_kernel, rbf_kernel, sigmoid_kernel, bagging,boosting, get_datasets, data_reconstruct, applyCorruption
from sklearn.utils import shuffle
import numpy as np
from feature_reduction import PCA
from feature_selection import feature_selection_filter_corr, select_feature
from hyperparam_tuning import hyperparam_tuning


def writeB(s):
    save = '/work/ratul1/chuen/temp/COM-S-573/LR_model/v2_BinomLR.txt'
    with open(save, 'a') as f:
        f.write(f'{s}')

def writeM(s):
    save = '/work/ratul1/chuen/temp/COM-S-573/LR_model/v2_MultiLR.txt'
    with open(save, 'a') as f:
        f.write(f'{s}')

# training and testing model functions
def training_test_model_bagging(technique,dataset_name,
        train_x, train_y, val_x, val_y, test_x, test_y, 
        l_rate1 = 0.001, no_iter1 = 100, best_prob1 = 0.5, l_rate2 = 0.001, no_iter2 = 100, best_prob2 = 0.5, 
        batch_size = 10, C = 1, num_models = 10):

        ws, bs, ls = bagging(train_x, train_y, val_x, val_y, C, batch_size, l_rate1, no_iter1, num_models, int(train_x.shape[0] / 3), 
                            model = LogisticRegression, model_type = 'binomial')
        score_test = ensemble_wrapper(test_x, test_y, ws, bs, False, 0.5,
                               model = LogisticRegression, model_type = 'binomial')
        score_train = ensemble_wrapper(train_x, train_y, ws, bs, False, 0.5,
                               model = LogisticRegression, model_type = 'binomial')
        writeB(f"{technique},{dataset_name},{score_test},{score_train}\n")
        
        ws, bs, ls = bagging(train_x, train_y, val_x, val_y, C, batch_size, l_rate2, no_iter2, num_models, int(train_x.shape[0] / 3), 
                            model = LogisticRegression, model_type = 'multinomial')
        score_test = ensemble_wrapper(test_x, test_y, ws, bs, False, 0.5,
                               model = LogisticRegression, model_type = 'multinomial')
        score_train = ensemble_wrapper(train_x, train_y, ws, bs, False, 0.5,
                               model = LogisticRegression, model_type = 'multinomial')
        writeM(f"{technique},{dataset_name},{score_test},{score_train}\n")

def training_test_model_boosting(technique,dataset_name,
        train_x, train_y, val_x, val_y, test_x, test_y, 
        l_rate1 = 0.001, no_iter1 = 100, best_prob1 = 0.5, l_rate2 = 0.001, no_iter2 = 100, best_prob2 = 0.5, 
        batch_size = 10, num_models = 10):

        ws, bs, ls, lWs = boosting(train_x, train_y, val_x, val_y, batch_size, l_rate1, no_iter1, num_models, int(train_x.shape[0] / 3), 
                            model = LogisticRegression, model_type = 'binomial')
        score_test = ensemble_wrapper(test_x, test_y, ws, bs, True, 0.5, accs = lWs,
                               model = LogisticRegression, model_type = 'binomial')
        score_train = ensemble_wrapper(train_x, train_y, ws, bs, True, 0.5, accs = lWs,
                               model = LogisticRegression, model_type = 'binomial')
        writeB(f"{technique},{dataset_name},{score_test},{score_train}\n")
        
        ws, bs, ls, lWs = boosting(train_x, train_y, val_x, val_y, batch_size, l_rate2, no_iter2, num_models, int(train_x.shape[0] / 3), 
                            model = LogisticRegression, model_type = 'multinomial')
        score_test = ensemble_wrapper(test_x, test_y, ws, bs, True, 0.5, accs = lWs,
                               model = LogisticRegression, model_type = 'multinomial')
        score_train = ensemble_wrapper(train_x, train_y, ws, bs, True, 0.5, accs = lWs,
                               model = LogisticRegression, model_type = 'multinomial')
        writeM(f"{technique},{dataset_name},{score_test},{score_train}\n")

def training_test_model(technique,dataset_name,
        train_x, train_y, val_x, val_y, test_x, test_y, 
        l_rate1 = 0.001, no_iter1 = 100, best_prob1 = 0.5, l_rate2 = 0.001, no_iter2 = 100, best_prob2 = 0.5):
    model = LogisticRegression(l_rate2, no_iter2)
    model.fit(train_x, train_y)
    score = model.score(test_x, test_y, prob= best_prob1)
    score2 = model.score(train_x, train_y, prob= best_prob1)
    writeB(f"{technique},{dataset_name},{score},{score2}\n")

    model1 = LogisticRegression(l_rate1, no_iter1, classifier="multinomial")
    model1.fit(train_x, train_y)
    score = model1.score(test_x, test_y, prob= best_prob2)
    score2 = model1.score(train_x, train_y, prob= best_prob1)
    writeM(f"{technique},{dataset_name},{score},{score2}\n")
'''
Normalization
Kernelization
Feature selection
Feature reduction
Shuffling
Bagging
Boosting
Hyperparameter-tuning
Data-reconstruction
Combination of the above techniques
'''
def basecase():
    #write("base case ---")
    #[[X_hw, y_hw], [X_bc, y_bc], [X_se, y_se], [X_wp, y_wp]]
    # index:    0-alzheimers, 1-breastcancer, 2-spamemail, 3-water-potability
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"base case,{key},")
        X = dataset[0]
        y = dataset[1]
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('base case', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def normalization():
    #write("normalization ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"normalization,{key},")
        X = dataset[0]
        y = dataset[1]

        X = normalize(X)

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('normalization', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def poly_kernelization():
    #write("poly kernelization ---")
    #[[X_hw, y_hw], [X_bc, y_bc], [X_se, y_se], [X_wp, y_wp]]
    # index:    0-alzheimers, 1-breastcancer, 2-spamemail, 3-water-potability
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"poly kernelization,{key},")
        X = dataset[0]
        y = dataset[1]

        X = poly_kernel(X, 1, 1, 2)

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('poly kernelization', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def rbf_kernelization():
    #write("rbf kernelization ---")
    #[[X_hw, y_hw], [X_bc, y_bc], [X_se, y_se], [X_wp, y_wp]]
    # index:    0-alzheimers, 1-breastcancer, 2-spamemail, 3-water-potability
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"rbf kernelization,{key},")
        X = dataset[0]
        y = dataset[1]

        X = rbf_kernel(X, 1)

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('rbf kernelization', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def sigmoid_kernelization():
    #write("sigmoid kernelization ---")
    #[[X_hw, y_hw], [X_bc, y_bc], [X_se, y_se], [X_wp, y_wp]]
    # index:    0-alzheimers, 1-breastcancer, 2-spamemail, 3-water-potability
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"sigmoid kernelization,{key},")
        X = dataset[0]
        y = dataset[1]

        X = sigmoid_kernel(X, 1, 1)

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('sigmoid kernelization', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def feature_selection():
    #write("feature selection ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"feature selection,{key},")
        X = dataset[0]
        y = dataset[1]

        try:
            # X = normalize(X) # <-- odd issue where this needs to be run first
            FS_filter = feature_selection_filter_corr(X, y)
            X_filter = select_feature(X, FS_filter)

            train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_filter, y, 0.8, 0.0, 0.2)
            training_test_model('feature selection', key,train_x, train_y, val_x, val_y, test_x, test_y)
        except:
            X = normalize(X) # <-- odd issue where this needs to be run first
            FS_filter = feature_selection_filter_corr(X, y)
            X_filter = select_feature(X, FS_filter)

            train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_filter, y, 0.8, 0.0, 0.2)
            training_test_model('feature selection', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def feature_reduction():
    #write("feature reduction ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"feature reduction,{key},")
        X = dataset[0]
        y = dataset[1]

        # X = normalize(X) # <-- odd issue where this needs to be run first
        try:
            X_pca = PCA(X, k=X.shape[1] * 0.2)

            train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_pca, y, 0.8, 0.0, 0.2)
            training_test_model('feature reduction', key,train_x, train_y, val_x, val_y, test_x, test_y)
        except:
            X = normalize(X) # <-- odd issue where this needs to be run first
            X_pca = PCA(X, k=X.shape[1] * 0.2)

            train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_pca, y, 0.8, 0.0, 0.2)
            training_test_model('feature reduction', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def shuffling():
    #write("shuffling ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"poly shuffling,{key},")
        X = dataset[0]
        y = dataset[1]
        
        X, y = shuffle(X, y)
        X, y = shuffle(X, y)
        X, y = shuffle(X, y)

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('shuffling', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def bagging_model():
    #write("bagging ---")
    datasets = get_datasets()

    '''
    key = 'Spam Email'
    dataset = datasets[key]
    #write(f"\nModel performance for: {key}")
    X = dataset[0]
    y = dataset[1]

    train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)

    training_test_model_bagging(train_x, train_y, val_x, val_y, test_x, test_y)
    '''

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"bagging,{key},")
        X = dataset[0]
        y = dataset[1]

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)

        training_test_model_bagging('bagging', key, train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def boosting_model():
    #write("boosting ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"boosting,{key},")
        X = dataset[0]
        y = dataset[1]

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)

        training_test_model_boosting('boosting', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def hyperparameter_tuning():
    #write("hyperparameter tuning ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"hyperparameter tuning,{key},")
        X = dataset[0]
        y = dataset[1]

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        
        l_rate1, no_iter1, best_prob1 = hyperparam_tuning(LogisticRegression, "multinomial", train_x, train_y)
        l_rate2, no_iter2, best_prob2 = hyperparam_tuning(LogisticRegression, "binomial", train_x, train_y)

        training_test_model('hyperparameter tuning', key,train_x, train_y, val_x, val_y, test_x, test_y, 
                            l_rate1, no_iter1, best_prob1, l_rate2, no_iter2, best_prob2)
    pass

def data_reconstruction():
    #write("data reconstruction ---")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"data reconstruction,{key},")
        
        X = dataset[0]
        y = dataset[1]

        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)

        #data corruption simulation for robustness
        train_x = applyCorruption(train_x, 0.5, 0.5, True)
        test_x = applyCorruption(test_x, 0.5, 0.5, True)

        #data reconstruction for corrupted data
        train_x = data_reconstruct(train_x, 0.25)
        test_x = data_reconstruct(test_x, 0.25)
    
        training_test_model('data reconstruction', key,train_x, train_y, val_x, val_y, test_x, test_y)
    pass

def combination():
    #write("combination_")
    datasets = get_datasets()

    for key in datasets:
        dataset = datasets[key]
        #write(f"\nModel performance for: {key}")
        #write(f"combination,{key},")
        X = dataset[0]
        y = dataset[1]

        X, y = shuffle(X, y)
        X, y = shuffle(X, y)
        X, y = shuffle(X, y)
        #write("--- basecase ---")
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('combination$BC', key,train_x, train_y, val_x, val_y, test_x, test_y)

        X = normalize(X)
        #write("--- add normalization ---")
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X, y, 0.8, 0.0, 0.2)
        training_test_model('combination$BC+N', key,train_x, train_y, val_x, val_y, test_x, test_y)

        FS_filter = feature_selection_filter_corr(X, y, remove_negative=True, minimum = X.shape[1])
        X_filter = select_feature(X, FS_filter)
        #write("--- add feature selection ---")
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_filter, y, 0.8, 0.0, 0.2)
        training_test_model('combination$BC+N+FS', key,train_x, train_y, val_x, val_y, test_x, test_y)
        
        X_pca = PCA(X_filter, k=2)
        #write("--- add feature reduction w/ FS ---")
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_pca, y, 0.8, 0.0, 0.2)
        training_test_model('combination$BC+N+FS+FR', key,train_x, train_y, val_x, val_y, test_x, test_y)
        
        #write("--- add hyperparameter tuning ---")
        l_rate1, no_iter1, best_prob1 = hyperparam_tuning(LogisticRegression, "multinomial", train_x, train_y)
        l_rate2, no_iter2, best_prob2 = hyperparam_tuning(LogisticRegression, "binomial", train_x, train_y)

        training_test_model('combination$BC+N+FS+FR+HT', key,train_x, train_y, val_x, val_y, test_x, test_y, 
                            l_rate1, no_iter1, best_prob1, l_rate2, no_iter2, best_prob2)

        #write("--- add bagging ---")
        training_test_model_bagging('combination$BC+N+FS+FR+HT+Bag', key, train_x, train_y, val_x, val_y, test_x, test_y)
        
        #write("--- add boosting ---")
        training_test_model_boosting('combination$BC+N+FS+FR+HT+HT+Boost', key,train_x, train_y, val_x, val_y, test_x, test_y)


        X_pca = PCA(X, k=X.shape[1] * 0.2)
        #write("--- add feature reduction w/o FS ---")
        train_x, train_y, val_x, val_y, test_x, test_y = splitData(X_pca, y, 0.8, 0.0, 0.2)
        training_test_model('combination$BC+N+FR', key,train_x, train_y, val_x, val_y, test_x, test_y)
        
        #write("--- add hyperparameter tuning w/o FS ---")
        l_rate1, no_iter1, best_prob1 = hyperparam_tuning(LogisticRegression, "multinomial", train_x, train_y)
        l_rate2, no_iter2, best_prob2 = hyperparam_tuning(LogisticRegression, "binomial", train_x, train_y)
        training_test_model('combination$BC+N+FR+HT', key,train_x, train_y, val_x, val_y, test_x, test_y, 
                            l_rate1, no_iter1, best_prob1, l_rate2, no_iter2, best_prob2)

        #write("--- add bagging w/o FS ---")
        training_test_model_bagging('combination$BC+N+FR+HT+Bag', key, train_x, train_y, val_x, val_y, test_x, test_y)
        
        #write("--- add boosting w/o FS ---")
        training_test_model_boosting('combination$BC+N+FR+HT+Boost', key, train_x, train_y, val_x, val_y, test_x, test_y)
    pass

if __name__ == "__main__":
    # basecase handwriting get 100% accuracy because
    # the pred value is too low, it turns into Nan
    # which predicts -1, and since there is no shuffle, all -1 data is at the end, hence 100%
    # this issue occurs similarly, until we test with it with shuffle. 

    # shuffle is needed to ensure realistic testing, imo
    basecase()              # 1 CHECK

    normalization()          # 2 CHECK
    poly_kernelization()     # 3 <-- ignore for now
    rbf_kernelization()     # 3 <-- ignore for now
    sigmoid_kernelization()     # 3 <-- ignore for now

    # current fix for below 2, is to try without normalize, except with normalize, 
    feature_selection()     # 4 <-- odd issue where it needs normalization first, 
    feature_reduction()     # 5 <-- similarly with #3

    shuffling()             # 6 CHECK

    # model will go too low of float, turns into Nan, and predicts all -1
    bagging_model()          # 7 CHECK
    boosting_model()         # 8 CHECK

    data_reconstruction()   # 9 CHECK
    hyperparameter_tuning() # 10 CHECK

    for i in range(10):
        #write(f"Round {i}")
        combination()           # 11 No combinations yet.
    pass