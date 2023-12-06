# Interpretable Clustering
## 實驗環境
**程式語言：** python

**套件：**
```
pip install numpy pandas matplotlib scikit-learn graphviz
```

**graphviz套件需另外處理：**
Windows
* 於 http://www.graphviz.org/download/ 下載graphviz
* 新增至環境變數
C:\Program Files (x86)\Graphviz2.38\bin
C:\Program Files (x86)\Graphviz2.38\bin\dot.exe

Ubuntu
```
sudo apt-get update
sudo apt-get install graphviz
pip install graphviz
```


## 資料集來源
1. Iris dataset
https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html#sklearn.datasets.load_iris
```
iris = load_iris()
data = iris.data
```
2. Dry Bean dataset (2020). UCI Machine Learning Repository. 
https://doi.org/10.24432/C50S4B.
3. Digits dataset
https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html#sklearn.datasets.load_digits
```
digits = load_digits()
data = digits.data
```
4. MNIST fsahion dataset
https://www.kaggle.com/datasets/zalando-research/fashionmnist/data

## 如何運行程式碼
**執行程式**
```
python interpretable_clustering.py
```