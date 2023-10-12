# A Comparative Visual Analytics Framework for Evaluating Evolutionary Processes in Multi-objective Optimization

This is the code repository for the IEEE VIS 2023 paper "A Comparative Visual Analytics Framework for Evaluating Evolutionary Processes in Multi-objective Optimization", an integrated visualization solution for analyzing evolutionary processes with comparative visual analytics methods.

Paper link: [`Arxiv Link`](https://arxiv.org/abs/2308.05640)

## Timeline

- **2023.10.10**: Code for the framework has been released.
- **2023.07.15**: The paper was accepted by IEEE VIS 2023.

## Introduction

Evolutionary multi-objective optimization (EMO) algorithms have been demonstrated to be effective in solving multi-criteria decision-making problems. In real-world applications, analysts often employ several algorithms concurrently and compare their solution sets to gain insight into the characteristics of different algorithms and explore a broader range of feasible solutions. However, EMO algorithms are typically treated as black boxes, leading to difficulties in performing detailed analysis and comparisons between the internal evolutionary processes. Inspired by the successful application of visual analytics tools in explainable AI, we argue that interactive visualization can significantly enhance the comparative analysis between multiple EMO algorithms. In this paper, we present a visual analytics framework that enables the exploration and comparison of evolutionary processes in EMO algorithms. Guided by a literature review and expert interviews, the proposed framework addresses various analytical tasks and establishes a multi-faceted visualization design to support the comparative analysis of intermediate generations in the evolution as well as solution sets. We demonstrate the effectiveness of our framework through case studies on benchmarking and real-world multi-objective optimization problems to elucidate how analysts can leverage our framework to inspect and compare diverse algorithms.

## Getting Started

Please download the [`data.zip`](https://osf.io/agqvh/) and extract the files into the `./backend/data` directory.

For deploying the frontend service, please refer to the [README file in `frontend`](./frontend).

For deploying the backend server, please refer to the [README file in `backend`](./backend).

## Citation

If you use or mention this work in your research, please consider the following BibTeX entry:

```BibTeX
@article{Huang2023emo,
archivePrefix = {arXiv},
arxivId = {2308.05640},
author = {Huang, Yansong and Zhang, Zherui and Jiao, Ao and Ma, Yuxin and Cheng, Ran},
journal = {IEEE Transactions on Visualization and Computer Graphics},
title = {A Comparative Visual Analytics Framework for Evaluating Evolutionary Processes in Multi-objective Optimization},
url = {http://arxiv.org/abs/2308.05640},
year = {2023}
}
```
