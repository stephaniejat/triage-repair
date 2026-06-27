## The role
### Bio
My background is in machine learning research focusing on world modelling, uncertainty quantification, dynamical systems, and operator-based views of learning systems, with a view to extend my work to exploring RL via optimal control. My strengths are on the more research and design heavy sides (e.g. designing tasks, verifiers, and reasoning about failure modes for OOD checks), rather than the purely packaging side of things: I often do need the help of coding agents to smooth out the packaging layer of a build, so this project is especially appealing to me. That said, I'm a quick and enthusiastic learner and am not one to shy away from a growth opportunity.

### Fit
Of the two roles, I would be best suited to building environments. Specifically, I would be able to contribute towards task/environment specification and stress-test reasoning, especially where the goal is to expose weak generalisation instead of just increasing task difficulty. I’d also be interested in helping to define what meaningful OOD testing should look like, both for specific environments and in a more general context, perhaps putting together some kind of OOD taxonomy/template. My academic work so far has mostly orbited the theme of generalisation in the face of non-conformity or asymmetry, making me a natural fit for work targeting soundness.

Of course, if necessary, I am capable of taking the lead in a project and do not require micro-management.

## The submission
### Idea
The environment package submitted targets a specific weakness in current iterations of frontier coding models, rather than a specific model. The best environments are not just "hard", but structured. This forces the agent to understand the underlying task dynamics in order to learn a good solution.

One of the first RL task contexts that came to mind was a sequential task in which downstream decision-making depends not only on point estimates but also on uncertainty. We find these task contexts in various domains: choosing the best mode of medical treatment, robot navigation, fraud review, inventory replenishment, etc.

`triage` uses a multi-step task to target the (in)ability of many frontier coding agents to preserve global latent invariants instead of just making a visible repair. The triage setting allows for clear distinction between surface plausibility and true accuracy, which requires the agent to grasp the behavioural contract between uncertainty, risk bands, and downstream escalation.

Depending on the environment, I think OOD can refer to any of the following shifts:
- Distribution of task instances.
- Sequence length/state trajectory.
- Available tools + interfaces.
- Assumptions a model can safely make from prior examples.

Pushing a model out of distribution in this context means requiring the agent to maintain a coherent internal state, instead of local pattern-matching. This environment distinguishes two OOD-like settings ([Lazebnik, 2026](https://doi.org/10.1007/s41060-025-00947-0)):
- Inside-OOD: inputs remain within the supported range, but unusual combinations should still affect escalation due to added uncertainty ([Heim & Frank, 2025](https://www.sei.cmu.edu/blog/out-of-distribution-detection-knowing-when-ai-doesnt-know/)).
- Outside-OOD: unsupported inputs should be routed to a safe fallback path instead of ordinary triage.

### Contamination Statement
The entire repository, from tests and verifier to individual functions, were written from scratch for the purpose of this trial. No real patient data was used (only synthetic data), and the code does not borrow from any prior client work, open source code platforms (e.g., stack overflow, Github etc.), or any of my own previously delivered code.

### Soundness
The verifier is designed to check more than just ordinary correctness via pattern-matching. It rejects fixes that satisfy only visible behaviour without respecting the underlying task dynamics, so that evidence for soundness is a core requirement of this build template. The repository includes `verifier/tests/`, which houses task tests, and `verifier/verify.py` which is the meta-verification logic.

A correct repair should preserve the following invariant set:
- unsupported inputs route to `fallback_review`,
- valid inputs compute adjusted risk correctly and output the correct escalation level,
- escalation depends on intended signal rather than cosmetic relabeling, and
- repeated calls do not mutate states in a way that will change future semantics.

Any patch that fails to preserve the target invariant cannot be counted as a true repair.

#### Hidden task tests
The held-back test assets enforce that:
- out-of-range inputs are handled correctly,
- escalation severity must be monotone in risk,
- higher uncertainty must never reduce escalation severity for the same base risk,
- repeated read-only evaluation must not mutate patient state, and
- the public summary, internal state, and escalation decision must agree.

#### Adversarial cheats
I tested the verifier with five separate shortcut strategies:
1. Alias: Interchanging the routing signal with the presentation label, introducing dependence where independence is required for learning true task dynamics.
2. Calibration: Using a shallow band-to-action mapping instead of the true routing signal.
3. Memorisation: hardcoding cases to regurgitate as output.
4. Summary: ad-hoc patching the pipeline output.
5. Threshold: adjusting thresholds to fit the error instead of fixing the underlying bug.

All were successfully rejected by the verifier.

#### Reward distribution
Scores were computed along five axes so that more complete solutions mean progressively higher scores:
1. Visible testing.
2. State consistency.
3. Uncertainty-aware escalation.
4. Read-only behaviour.
5. Hidden-test robustness.

A capability ladder is supported by **graded reward density**:
```python
    # Gradient score policy
    if not axes["visible_axis"]:
        score = 0.0 # visible tests fail.
    elif not axes["consistency_axis"]:
        score = 0.25 # visible tests pass, but states are inconsistent.
    elif not axes["uncertainty_axis"]:
        score = 0.50 # states match, but uncertainty logic is still wrong.
    elif not axes["mutation_axis"]:
        score = 0.75 # uncertainty logic is fixed, but repeated calls mutate state.
    elif not axes["robustness_axis"]:
        score = 0.90 # state is read-only + visible, most hidden tests pass.
    else:
        score = 1.0 # all visible and hidden checks pass, no cheats detected.
```

### Learnings
It was important for `scoring.py` and `routing.py` to stay independent of each other: the former is the source of truth for numeric adjustment, while the latter is the source of truth for label-mapping. In the first draft of the repository, I had repeated the risk-adjustment function in `routing.py`, muddying the waters between the two layers and creating an architectural mismatch with the invariant. Luckily, the verifier caught my 'bad repair'.

The more meta mistake I made which caused the confusion was launching into coding the repository too quickly, when I should have taken pen to paper first, and clarified the task dynamics in detail before starting.

### Template
I liked how clear the template was about what the project is looking for in terms of deliverables, and its emphasis on proving, not just asserting, soundness. One thing I found confusing when going through the template is that the last section reads like an afterthought: since they are "not optional extras", they may be better placed right after the 3 tier guidelines, before the checklist summary. Sections 1-3 have some repeated points which make it less clear for someone reading the template and looking to produce work that explicitly meets the requirements. I also think that soundness and statistics should be 2 different layers: one is achievable with adversarial and hidden tests, relatively contained to the designer/engineer; the other depends on repeated runs with data, extending the testing beyond design logic.