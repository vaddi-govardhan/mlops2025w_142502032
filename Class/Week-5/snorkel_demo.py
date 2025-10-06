from datasets import load_dataset 
import pandas as pd 
 
# Load 2000 training and 500 test examples for speed 
 
imdb = load_dataset("imdb") 
train = pd.DataFrame(imdb["train"].select(range(2000))) 
test  = pd.DataFrame(imdb["test"].select(range(500))) 
print("Train size:", len(train), "Test size:", len(test)) 
train.head()



import re 
def clean_text(text): 
    text = re.sub(r"<br\s*/?>", " ", text) 
    text = re.sub(r"[^\w\s']", "", text) 
    return text.lower() 
 
train["text"] = train["text"].apply(clean_text) 
test["text"]  = test["text"].apply(clean_text) 




from snorkel.labeling import labeling_function, LFAnalysis 
from snorkel.labeling.model import LabelModel 
 
ABSTAIN, NEG, POS = -1, 0, 1 
positive_words = {"great","excellent","amazing","wonderful","best","fantastic"} 
negative_words = {"bad","terrible","awful","worst","boring","poor"} 
 
@labeling_function() 
def lf_positive(x): 
    return POS if any(w in x.text.split() for w in positive_words) else ABSTAIN 
 
@labeling_function() 
def lf_negative(x): 
    return NEG if any(w in x.text.split() for w in negative_words) else ABSTAIN 
 
@labeling_function() 
def lf_exclaim(x): 
    return POS if x.text.count("!") > 2 else ABSTAIN 
lfs = [lf_positive, lf_negative, lf_exclaim] 





from snorkel.labeling import PandasLFApplier 
applier = PandasLFApplier(lfs) 
L_train = applier.apply(train) 
LFAnalysis(L_train, lfs).lf_summary() 



label_model = LabelModel(cardinality=2, verbose=True) 
label_model.fit(L_train=L_train, n_epochs=500, log_freq=100, seed=42) 
 
# Get probabilistic labels 
train_probs = label_model.predict_proba(L_train) 
train_preds = label_model.predict(L_train) 



from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import classification_report 
 
# Vectorize 
 
vectorizer = TfidfVectorizer(max_features=5_000) 
X_train = vectorizer.fit_transform(train["text"]) 

y_train = train_preds
clf = LogisticRegression(max_iter=200)
clf.fit(X_train, y_train)
 
# Evaluate on test set 
 
X_test = vectorizer.transform(test["text"]) 
y_test = test["label"] 
preds = clf.predict(X_test) 
print(classification_report(y_test, preds, labels=[0,1], target_names=["neg","pos"]))

