import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os
from scipy.spatial.distance import cdist


def plotGraph(G):
    # 使用spring_layout为图的节点提供一个美观的布局
    pos = nx.spring_layout(G)

    # 绘制图的边和节点
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')

    # 绘制节点的标签
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='Arial')

    # 显示图形
    plt.axis('off')  # 关闭坐标轴
    plt.show()


def matrixCreate(n_nodes, avg_degree):
    # 生成一个N个节点的随机图

    # 使用Erdos-Renyi随机图模型生成图
    # 该模型会随机选择节点对并添加边，直到达到预期的平均度数
    G = nx.erdos_renyi_graph(n=n_nodes, p=avg_degree / (n_nodes - 1))

    # 从图中导出邻接矩阵
    adjacency_matrix = nx.adjacency_matrix(G)

    # 将稀疏矩阵转换为numpy数组，这样我们可以更方便地查看和处理它
    adjacency_matrix = adjacency_matrix.toarray()

    # 随机化节点之间的距离
    for i in range(n_nodes):
        for j in range(n_nodes):
            if adjacency_matrix[i][j] == 1:
                # 在这里你可以根据需要调整距离的范围，例如使用np.random.uniform(1, 10)生成1到10之间的随机数
                adjacency_matrix[i][j] = np.random.randint(1, 5)  # 生成1到5之间的随机整数作为距离

    return adjacency_matrix, G


def kmeans_clustering(adj_matrix, num_clusters):
    # 获取节点数量
    num_nodes = adj_matrix.shape[0]

    # 将邻接矩阵转换为节点特征矩阵
    node_features = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(num_nodes):
            if adj_matrix[i][j] != 0:
                node_features[i][j] = 1

    # 使用KMeans进行聚类
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(node_features)
    cluster_labels = kmeans.labels_

    # 为每个簇选择连接度最高的节点作为簇首
    new_centroids = []
    for i in range(num_clusters):
        # 筛选出当前簇的所有节点
        cluster_nodes = np.where(cluster_labels == i)[0]

        # 计算每个节点的连接度
        node_degrees = np.sum(adj_matrix[cluster_nodes, :], axis=1)

        # 选择连接度最高的节点作为簇首
        max_degree_idx = np.argmax(node_degrees)
        new_centroids.append(cluster_nodes[max_degree_idx])

    return cluster_labels, new_centroids


def calculate_distances(cluster_labels, centroid_ids, node_features):
    num_clusters = len(np.unique(cluster_labels))
    distance_dicts = []
    average_distances = []  # 用来存储每个簇的平均距离

    for i in range(num_clusters):
        cluster_nodes = node_features[cluster_labels == i]
        centroid = node_features[centroid_ids[i]]

        if cluster_nodes.shape[0] > 0:
            # 计算簇首到每个节点的距离
            dist = cdist(centroid.reshape(1, -1), cluster_nodes)

            # 创建一个字典，包含节点编号和对应的距离
            distance_dict = {node_id: dist[0][j] for j, node_id in enumerate(np.where(cluster_labels == i)[0])}
            distance_dicts.append(distance_dict)

            # 计算并存储该簇的平均距离
            average_distance = np.mean(dist)
            average_distances.append(average_distance)
        else:
            # 如果簇中没有其他节点，创建一个空字典，并将平均距离设置为0
            distance_dicts.append({})
            average_distances.append(0)

    return distance_dicts, average_distances  # 返回包含平均距离的列表


def DynamicClustering(adj_matrix, distance_threshold):
    num_clusters = 1
    g_avg_distances = np.inf  # 初始化为无穷大，确保至少有一次迭代

    while g_avg_distances > distance_threshold:
        cluster_labels, centroids = kmeans_clustering(adj_matrix, num_clusters)
        distances, average_distances = calculate_distances(cluster_labels, centroids, adj_matrix)
        g_avg_distances = np.mean(average_distances)

        # 如果平均距离大于阈值，增加簇的数量并重新迭代
        if g_avg_distances > distance_threshold:
            num_clusters += 1

    return cluster_labels, centroids, distances, average_distances


if __name__ == '__main__':
    adjacency_matrix, G = matrixCreate(100, 5)
    # print(adjacency_matrix)
    num_clusters = 5
    cluster_labels, centroids, distances, average_distances = DynamicClustering(adjacency_matrix, 8)

    print("分簇结果：", cluster_labels)
    print("簇中心：", centroids)
    print("距离：", distances)
    print("平均距离：", average_distances)
