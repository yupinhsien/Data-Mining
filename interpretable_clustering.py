# -*- coding: utf-8 -*-
"""Interpretable_Clustering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VqCBLjNSY18Y3ovN0OKQ7o1wNRaGegEO

Import library
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.tree import DecisionTreeClassifier, export_text, _tree
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn import tree

from scipy.spatial.distance import cdist

import graphviz

import random

# Load the Digits dataset
digits = load_digits()
data = digits.data

"""FUNCTIONS"""

def calculate_weights_array(k, centroids, num_features):
    weights_list = []

    for i in range(k):
        for j in range(i + 1, k):
            weight_data = [2 * (centroids[j][feature] - centroids[i][feature]) for feature in range(num_features)]
            weights_list.append(np.array(weight_data))

    return np.array(weights_list)

def extract_features_and_rows(tree, weights_array):
    tree_ = tree.tree_

    rows_and_features = []

    def recurse(node):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            feature_index = tree_.feature[node]
            feature_used = f'X_{feature_index}'

            threshold = tree_.threshold[node]

            # Extract the corresponding row from weights_array
            row_index = feature_index
            row_data = weights_array[row_index]

            # Append to the list
            rows_and_features.append({
                'Feature': feature_used,
                'Threshold': threshold,
                'RowData': row_data
            })

            recurse(tree_.children_left[node])
            recurse(tree_.children_right[node])  # Include right branch for completeness

    recurse(0)

    return rows_and_features

# function of loss function
def loss_function(Z, T_X_theta, lambda_mu, decision_nodes):
    square_error = np.sum((Z-T_X_theta) ** 2)

    L1_norm = sum([np.linalg.norm(w, ord=1) for w in decision_nodes])

    return square_error + lambda_mu * L1_norm

# function of optimization of the weights
def compute_gradient(Z, T_X_theta, decision_nodes):
    square_error_gradient = np.zeros_like(decision_nodes)
    L1_norm_gradient = np.zeros_like(decision_nodes)
    for i in range(len(decision_nodes)):
        for j in range(len(decision_nodes[i])):
            if decision_nodes[i][j] > 0:
                L1_norm_gradient[i][j] += 1
            elif decision_nodes[i][j] < 0:
                L1_norm_gradient[i][j] -= 1
            square_error_gradient[i][j] = 2 * (Z[j] - T_X_theta[j])
    return square_error_gradient + L1_norm_gradient

# define k-means
class KMeansCustom:
    def __init__(self, n_clusters, max_iter=500):
        self.n_clusters = n_clusters
        self.max_iter = max_iter

    def fit(self, data,tree,mu):
        self.centroids = []
        # initialize centroids
        for _ in range(self.n_clusters):
            self.centroids.append(data[random.randint(0, len(data) - 1)])

        for _ in range(self.max_iter):
            clusters = {}
            for i in range(self.n_clusters):
                clusters[i] = []

            # clustering
            for i, point in enumerate(data):
                distances = [np.linalg.norm(point - centroid)+mu*(j - tree[i]) ** 2 for j, centroid in enumerate(self.centroids)]

                cluster = distances.index(min(distances))
                clusters[cluster].append(point)

            # update centroids
            for cluster in clusters:
                self.centroids[cluster] = np.average(clusters[cluster], axis=0)

        self.labels_ = np.zeros(len(data))

        # assign labels
        for i, point in enumerate(data):
            distances = [np.linalg.norm(point - centroid)+mu*(j - tree[i]) ** 2 for j, centroid in enumerate(self.centroids)]
            self.labels_[i] = distances.index(min(distances))

    def predict(self, data):
        labels = np.zeros(len(data))

        # assign labels
        for i, point in enumerate(data):
            distances = [np.linalg.norm(point - centroid)+mu*(j - tree[i]) ** 2 for j, centroid in enumerate(self.centroids)]
            labels[i] = distances.index(min(distances))

        return labels

    def get_centroids(self):
        return self.centroids

# Calculate the sum of squared distances (inertia) for the KMeansCustom clustering
def calculate_objective_function(data, centroids, labels):
    total_distance = 0
    for i, point in enumerate(data):
        centroid = centroids[int(labels[i])]  # Centroid assigned to the point
        total_distance += np.linalg.norm(point - centroid) ** 2  # Squared distance to centroid
    return total_distance

"""INPUT"""

lambda_ = 100.0
a = 1.1
mu_0 = 1
learning_rate = 0.01

# Specify the number of clusters (k)
k = 10

n_initialization = 50
max_iteration = 500

"""FREE CLUSTERING"""

# Perform k-means clustering
kmeans = KMeans(n_clusters=k, random_state=42, n_init = n_initialization, max_iter = max_iteration)
kmeans.fit(data)
centroids = kmeans.cluster_centers_

centroids

Z = kmeans.predict(data)

# Calculate objective function for training data
objective_function = calculate_objective_function(data, centroids, Z)
print(f"Objective function: {objective_function}")

num_features = data.shape[1]

weights_array = calculate_weights_array(k, centroids, num_features)

# Perform dot product using np.dot
diff_centroids = np.dot(data, np.transpose(weights_array))

"""DIRECT TREE FIT"""

class_unique = np.unique(Z)
class_name_list = [str(element) for element in class_unique]

clf = DecisionTreeClassifier(max_depth = 5)
model = clf.fit(diff_centroids, Z)

dot_data = tree.export_graphviz(clf, out_file=None,
                                class_names = class_name_list,
                                filled=True, rounded = True)

# Draw graph
graph = graphviz.Source(dot_data, format="png")

# Save the graph as a PNG file
graph.render("decision_tree", format="png", cleanup=True)

graph

T_X_theta = clf.predict(diff_centroids)

# Count the differences between two arrays
differences_count = np.count_nonzero(Z != T_X_theta)

# Display the result
print(f"Number of differences: {differences_count}")

"""WEIGHTS OF DECISION NODES"""

decision_nodes_info = extract_features_and_rows(clf, weights_array)

# Create a 2D array with all the row data
decision_weights = np.array([info['RowData'] for info in decision_nodes_info])

mu = mu_0

"""TAO - OPTIMIZING WEIGHTS"""

iterations = 10

# theta = decision_weights

# # gradient descent iterations
# lambda_mu = lambda_ / mu
# for i in range(iterations):
#     # compute the loss and gradient descent
#     current_loss = loss_function(Z, T_X_theta, lambda_mu, theta)

#     gradient = compute_gradient(Z, T_X_theta, theta)

#     # optimize the weights of the decision nodes
#     for j in range(len(theta)):
#         theta[j] -= learning_rate * gradient[j]

#     # import current loss
#     print(f"Iteration {i}: Loss = {current_loss}")

# print(f"Optimized decision weights: \n{theta}")
# mu *= a
# print(mu)

"""OPTIMIZE TREE ACCORDING TO THE OPTIMIZED WEIGHTS"""

# optimized_distance = np.dot(data, np.transpose(theta))

# model = clf.fit(optimized_distance, Z)

# T_X_theta = clf.predict(optimized_distance)

# # Count the differences between two arrays
# differences_count = np.count_nonzero(Z != T_X_theta)

# # Display the result
# print(f"Number of differences: {differences_count}")

"""





CLUSTERING & DECISION TREE ITERATIONS"""

kmeans_custom = KMeansCustom(n_clusters=k)
i=1
differences_count_array = []

kmeans_custom = KMeansCustom(n_clusters=k)

while(1):
    print(i)
    kmeans_custom.fit(data,T_X_theta,mu)
    Z = kmeans_custom.labels_
    centroids = kmeans_custom.get_centroids()

    weights_array = calculate_weights_array(k, centroids, num_features)

    diff_centroids = np.dot(data, np.transpose(weights_array))

    model = clf.fit(diff_centroids, Z)
    T_X_theta = clf.predict(diff_centroids)
    differences_count = np.count_nonzero(Z != T_X_theta)
    print(differences_count)

    if differences_count == 0:
        print("Converged: No differences.")
        break

    decision_nodes_info = extract_features_and_rows(clf, weights_array)
    decision_weights = np.array([info['RowData'] for info in decision_nodes_info])
    theta = decision_weights

    # gradient descent iterations
    for j in range(iterations):
        # compute the loss and gradient descent
        lambda_mu = lambda_ / mu
        current_loss = loss_function(Z, T_X_theta, lambda_mu, theta)

        gradient = compute_gradient(Z, T_X_theta, theta)

        # optimize the weights of the decision nodes
        for l in range(len(theta)):
            theta[l] -= learning_rate * gradient[l]

        # import current loss
        # print(f"Iteration {i}: Loss = {current_loss}")

    # print(f"Optimized decision weights: \n{theta}")
    mu *= a
    # print(mu)

    optimized_distance = np.dot(data, np.transpose(theta))
    model = clf.fit(optimized_distance, Z)

    T_X_theta = clf.predict(optimized_distance)
    differences_count = np.count_nonzero(Z != T_X_theta)
    differences_count_array.append(differences_count)
    print(differences_count)

    if differences_count <= 0:
        print("Converged: No differences.")
        break
    i=i+1

# 生成 x 軸的數據，索引加 1
x = np.arange(1, len(differences_count_array) + 1)

# 繪製折線圖
plt.plot(x, differences_count_array, marker='o')

# 添加標籤
plt.xlabel('Iteration')
plt.ylabel('Difference point')

# 添加標題
# plt.title('dry bean dataset')

# 顯示圖表
plt.show()

print(centroids)

dot_data = tree.export_graphviz(clf, out_file=None, class_names = class_name_list, filled=True, rounded = True)

# Draw graph
graph = graphviz.Source(dot_data, format="png")

# Save the graph as a PNG file
graph.render("replaced_decision_tree", format="png", cleanup=True)

graph