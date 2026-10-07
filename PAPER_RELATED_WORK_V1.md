# Related Work draft for Kaggle Writeup

Repository-level software-engineering benchmarks such as **SWE-bench** evaluate whether a system can resolve real GitHub issues across large codebases, making repository interaction and multi-file reasoning first-class evaluation problems [1]. **SWE-agent** further shows that agent-computer interface design materially changes an LM agent's ability to navigate repositories, edit files, and execute tests [2]. **OpenHands** provides a broad open platform for software-development agents, including sandboxed execution, multi-agent coordination, tool use, and benchmark integration [3].

Other work questions whether increasingly complex agent loops are always necessary. **Agentless** demonstrates that a simpler localization–repair–validation pipeline can be competitive, motivating explicit ablations rather than assuming that more orchestration is inherently better [4]. Repository-structure methods such as **RepoGraph** improve context selection by exposing repository-level code relationships to SWE systems [5].

Our work is complementary to these directions. We do not propose a replacement for repository retrieval, code graphs, agent-computer interfaces, or model adaptation. Instead, we focus on a different failure surface: whether an otherwise capable system is allowed to mutate canonical repository state when its starting state is stale, another writer has intervened, a tool partially failed, a session rolled over, or verification evidence is incomplete. The proposed contribution is therefore a **control-plane architecture**: read-only observation, bounded execution, independent verification, immutable predeclared acceptance, evidence-bound receipts, single-writer semantics, and atomic fail-closed promotion.

This distinction motivates our A–F ablation. The experiment is designed not only to measure issue completion, but also stale promotions, duplicate work, invalid mutations, rollbacks, verification overhead, and false GREEN outcomes.

## References

1. Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, and Karthik Narasimhan. **SWE-bench: Can Language Models Resolve Real-World GitHub Issues?** ICLR 2024. https://arxiv.org/abs/2310.06770
2. John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, and Ofir Press. **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.** 2024. https://arxiv.org/abs/2405.15793
3. Xingyao Wang et al. **OpenHands: An Open Platform for AI Software Developers as Generalist Agents.** 2024. https://arxiv.org/abs/2407.16741
4. Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, and Lingming Zhang. **Agentless: Demystifying LLM-based Software Engineering Agents.** 2024. https://arxiv.org/abs/2407.01489
5. Siru Ouyang et al. **RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph.** 2024. https://arxiv.org/abs/2410.14684
