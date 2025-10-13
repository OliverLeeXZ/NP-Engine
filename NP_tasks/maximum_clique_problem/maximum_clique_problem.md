## Description
Given an undirected graph G=(V,E), where V is a set of vertices and E is a set of edges, the Maximum Clique Problem (MCP) asks for the largest complete subgraph (clique) in the graph, or determines whether a given size clique exists in the graph. A complete subgraph (clique) is one where every two distinct vertices are adjacent, i.e., there is an edge between every pair of vertices in the clique. The goal is to find the complete subgraph (clique) in the graph, make the size of the clique as large as possible. You can start by finding the smallest clique first.


## Submission Format
The answer should be a list of integers representing the vertices that form the largest clique. The list must represent a valid clique, meaning that each pair of vertices in the list must be connected by an edge in the graph. The output should be in the following format (as an example): [0, 1, 3, 4]. This example means that vertices 0, 1, 3 and 4 form a clique in the graph, and its size is 4.

## Example Input
```
0: [1, 2, 3, 4]
1: [0, 3, 4]
2: [0, 3]
3: [0, 1, 2, 4]
4: [0, 1, 3]
```
## Example Output
```
Answer: [0, 1, 3, 4]
```



