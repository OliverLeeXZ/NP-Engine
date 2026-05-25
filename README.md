# Forge: Quality-Aware Reinforcement Learning for NP-Hard Optimization in LLMs

<div align="center">

[📃[Paper](https://arxiv.org/abs/2605.08905)]
[🌐[Project Page](https://github.com/OliverLeeXZ/NP-Engine)]
[🤗[Model](https://huggingface.co/OliverLee/Qwen2.5-7B-NP)]
</div>

## 📣 What's New
- **[2026.5.25]** We release our training data in [OliverLee/NP](http://huggingface.co/datasets/OliverLee/NP). 🎉🎉🎉
- **[2026.5.8]** We updated NP-Engine by training it from a reasoning model and incorporating more RL algorithms. Check it out at 📃 [arXiv: Forge](https://arxiv.org/abs/2605.08905)!
- **[2026.4.6]** The Forge (NP-Engine) has been accepted at **ACL 2026**! See you in **San Diego**! 🎉🎉🎉
- **[2025.10.14]** We have released NP-Bench in [OliverLeeXZ/NP-Engine](https://github.com/OliverLeeXZ/NP-Engine). 🎉🎉🎉
- **[2025.10.13]** We have released model checkpoint in [OliverLee/Qwen2.5-7B-NP](https://huggingface.co/OliverLee/Qwen2.5-7B-NP). 🎉🎉🎉
- **[2025.6.10]** Our NP-Engine Paper is released! Check it at 📃[Arxiv: NP-Engine](https://arxiv.org/abs/2510.16476) ! Our Dataset will be open-sourced soon! 🎉🎉🎉

## 👨‍💻 Todo List

- ✅ Paper Release
- ✅ Checkpoint Release
- ✅ NP-Bench Release
- ✅ RLVR Training Code Release
- ✅ Training Data Release



## 🌟 Highlights
<div align="center">
 <img src="./images/webpages/spotlight.png" width="800"/>
</div>

NP-ENGINE evaluates and trains reasoning models on **10 NP-hard optimization tasks** across five categories, including **subset selection** and **path planning**. Its automated pipeline—composed of a **Data Generator**, **Solution Validator**, and **Heuristic Solver**—enables controllable data synthesis, rigorous evaluation, and scalable training. A case study on **Hamiltonian Circuit** demonstrates the model’s ability to find optimal solutions, while OOD evaluations show improved general reasoning capabilities beyond the training tasks.

- **We introduce NP-ENGINE**, a scalable framework that generates near-infinite and hierarchically difficult NP-hard problems within the RLVR paradigm, empowering LLMs' optimization reasoning abilities. NP-ENGINE enables Qwen2.5-7B-Instruct to significantly outperform GPT-4o in optimization reasoning tasks using only 5K training examples.

- **We propose NP-BENCH**, a benchmark consisting of 10 NP-level tasks spanning five categories: Graph Clustering, Resource Scheduling, Graph Partitioning, Subset Selection, and Path Planning. NP-BENCH provides instances with varying difficulty levels and evaluates both the feasibility and quality of solutions.

- **Through extensive experiments**, we demonstrate that training on NP-ENGINE-DATA enables QWEN2.5-7B-NP to generalize to both reasoning and non-reasoning OOD tasks. We also observe a positive correlation between task diversity and cross-task generalization performance, offering new insights into the scaling behavior of RLVR-based training.

## 📚 Dataset Statistics

<div align="center">
 <img src="./images/webpages/data.png" width="800"/>
</div>

## 🏆 NP-Bench Leaderboard
## Performance of reasoning LLMs, general LLMs, and our trained LLMs on \bench.

| **Model**              | **Graph SR** | **Graph AR** | **Schedule SR** | **Schedule AR** | **Partition SR** | **Partition AR** | **Selection SR** | **Selection AR** | **Planning SR** | **Planning AR** | **Overall SR** | **Overall AR** |
|------------------------|--------------|--------------|-----------------|-----------------|------------------|------------------|------------------|------------------|-----------------|-----------------|----------------|----------------|
| **Proprietary LLMs**    |              |              |                 |                 |                  |                  |                  |                  |                 |                 |                |                |
| DS-V3.1-Thinking        | 86.0         | 78.2         | **99.0**        | 91.4            | 98.0             | **77.1**         | **99.3**         | **98.5**         | 61.9            | 54.3            | 88.8           | **79.9**       |
| gpt-o3                  | **97.0**     | **86.4**     | **99.0**        | **94.5**        | **100.0**        | 51.4             | 87.4             | 87.3             | 74.0            | **65.1**        | 91.5           | 76.9           |
| Qwen3-235B-Thinking     | 66.7         | 62.9         | 95.0            | 93.0            | **100.0**        | 55.8             | 98.0             | 97.1             | 52.0            | 44.8            | 82.3           | 70.7           |
| gpt-4o-2024-08-06      | 64.7         | 29.3         | 79.0            | 59.8            | **100.0**        | 53.0             | 14.7             | 9.3              | 52.0            | 29.6            | 62.1           | 36.2           |
| **Open-Source LLMs**    |              |              |                 |                 |                  |                  |                  |                  |                 |                 |                |                |
| Qwen3-32B               | 44.7         | 39.3         | 94.0            | 93.9            | 99.0             | 52.6             | 94.1             | 91.4             | 21.6            | 11.2            | 70.7           | 57.6           |
| Qwen3-8B                | 22.7         | 16.8         | 78.0            | 75.3            | 98.0             | 51.0             | 86.0             | 82.6             | 3.0             | 1.2             | 57.5           | 45.4           |
| DS-R1-Qwen-32B          | 23.3         | 18.1         | 49.0            | 45.1            | 96.0             | 48.6             | 85.7             | 79.7             | 15.4            | 7.9             | 53.9           | 39.9           |
| DS-R1-Qwen-14B          | 18.0         | 13.4         | 52.0            | 51.7            | 32.0             | 16.2             | 67.3             | 63.4             | 4.5             | 1.4             | 34.8           | 29.2           |
| Qwen2.5-72B             | 34.7         | 15.2         | 59.0            | 58.5            | 90.0             | 39.5             | 27.0             | 17.4             | 6.5             | 2.1             | 43.4           | 26.5           |
| Qwen2.5-32B             | 35.3         | 15.2         | 15.0            | 12.8            | **100.0**        | 51.7             | 32.0             | 22.4             | 23.5            | 6.7             | 41.2           | 21.8           |
| Qwen2.5-14B             | 30.0         | 11.5         | 21.0            | 15.8            | 89.0             | 44.3             | 23.3             | 12.7             | 17.5            | 4.9             | 36.2           | 17.8           |
| InternLM3-8b            | 15.0         | 3.6          | 20.0            | 9.5             | 86.0             | 43.3             | 41.3             | 23.7             | 16.0            | 4.1             | 35.7           | 16.8           |
| LLama3.1-8B             | 23.0         | 8.0          | 9.0             | 7.8             | 0.0              | 0.0              | 28.7             | 11.4             | 15.0            | 1.8             | 15.1           | 5.8            |
| Qwen2.5-3B              | 7.7          | 2.9          | 17.0            | 5.0             | 6.0              | 2.2              | 23.0             | 10.7             | 15.5            | 3.7             | 13.8           | 4.9            |
| DS-R1-Qwen-7B           | 6.3          | 1.9          | 1.0             | 0.9             | 2.0              | 1.0              | 13.7             | 8.9              | 0.5             | 0.1             | 4.7            | 2.5            |
| Qwen2.5-7B              | 11.0         | 3.1          | 40.0            | 19.8            | 67.0             | 34.0             | 26.7             | 15.2             | 3.5             | 1.0             | 29.6           | 14.6           |
| **Model**               | **89.7**     | **27.8**     | **85.0**        | 43.5            | **99.0**          | **53.8**         | **93.7**         | **79.1**         | **98.2**         | **28.9**         | **93.1**        | **46.6**        |
| **Delta**               | +78.7        | +24.7        | +45.0           | +23.7           | +32.0            | +19.8            | +67.0            | +63.9            | +94.7            | +27.9            | +63.5           | +32.0           |


## Setup



## 🖊️ Citation

If you find this work helpful, please consider to **star🌟** this repo and cite this paper. Thanks for your support!

```bib
@misc{li2026forgequalityawarereinforcementlearning,
      title={Forge: Quality-Aware Reinforcement Learning for NP-Hard Optimization in LLMs}, 
      author={Xiaozhe Li and Xinyu Fang and Shengyuan Ding and Yang Li and Linyang Li and Haodong Duan and Qingwen Liu and Kai Chen},
      year={2026},
      eprint={2605.08905},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2605.08905}, 
}
```

<!-- <picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="
      https://api.star-history.com/svg?repos=OliverLeeXZ/NP-Engine&type=Date&theme=dark
    "
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="
      https://api.star-history.com/svg?repos=OliverLeeXZ/NP-Engine&type=Date
    "
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=OliverLeeXZ/NP-Engine&type=Date"
  />
</picture> -->