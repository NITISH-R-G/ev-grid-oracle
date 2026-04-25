# Theme templates (OpenEnv Hackathon)

Use these as **idea generators**. Each template is deliberately structured to produce:
- partial observability
- tool-driven interaction
- learnable reward signals
- obvious “before vs after training” demos

## Theme 1: Multi-agent interactions

### T1-A: Compute-allocation negotiation (private values)
- **Agents**: requester(s), allocator, auditor (optional)
- **Hidden state**: true urgency, private utility curves, hidden constraints (maintenance windows)
- **Observation**: budget announcements, partial usage logs, noisy latency probes
- **Actions**: propose allocations, counter-offers, message other agents, commit/finalize
- **Reward**:
  - allocator: efficiency + fairness + constraint satisfaction
  - requester: achieved QoS vs spend
  - negotiation quality: Pareto improvement vs baseline split
- **Anti-gaming**: detect lying via consistency checks between claimed needs and observed usage; cap “spam messaging”

### T1-B: Coalition formation (shifting incentives)
- **Agents**: 4–6 “departments” bidding for shared resources
- **Hidden state**: each has a secret project payoff; one has a sabotage incentive
- **Actions**: propose coalition, share partial proofs, vote, sign contracts
- **Reward**:
  - coalition value realized (true payoff) minus instability penalties
  - penalty for broken promises / contradictions across messages

### T1-C: Mixed coop/comp strategy game (partially observable)
- **Agents**: two teams with shared constraint (e.g., power grid stability) but competing KPI
- **Hidden state**: adversary plan + random shocks
- **Actions**: dispatch, load shedding proposals, “information purchase”
- **Reward**: keep global constraint satisfied + team KPI; penalize myopic wins that cause later collapse

## Theme 2: (Super) long-horizon planning & instruction following

### T2-A: “OpenClaw-style” long project with amnesia + external memory
- **World**: multi-stage project with 200–300 micro-instructions scattered across docs
- **Constraint**: periodic context truncation; external scratchpad has a cost per write/read
- **Actions**: search/read docs, update plan, execute steps, checkpoint, rollback
- **Reward**:
  - shaped: completion of verified subgoals
  - terminal: project delivered + acceptance tests
  - penalties: unnecessary tool calls, repeated mistakes, inconsistent state

### T2-B: Logistics optimization with delayed reward
- **World**: routing + inventory + time windows across 50–200 steps
- **Hidden state**: future demand shocks, road closures revealed late
- **Actions**: plan, commit routes, hedge with buffers, purchase forecasts
- **Reward**:
  - sparse: total cost at end
  - dense: constraint satisfaction, forecast calibration, regret vs oracle

## Theme 3: World modeling

### T3.1-A: Dynamic enterprise app simulator (tickets → code → deploy)
- **World**: simulated product backlog with flaky integration tests and drifting requirements
- **Tools**: “issue tracker”, “CI logs”, “customer emails”, “deploy dashboard”
- **Hidden state**: true root cause, user priorities, org constraints
- **Reward**:
  - solve correct issues, reduce regression rate
  - consistency: claims in updates must match logs

### T3.2-A: Executive assistant with conflicts + social constraints
- **World**: calendar, emails, preferences, relationships, hidden constraints (privacy)
- **Hidden state**: unstated preferences (don’t schedule late), latent stress, travel time realism
- **Actions**: propose plan, ask clarification (limited), message stakeholders, reschedule
- **Reward**:
  - satisfaction across stakeholders (latent)
  - constraint satisfaction (time, travel)
  - communication quality rubric (tone, clarity, brevity)

## Theme 4: Self-improvement

### T4-A: Task generator + verifier loop
- **World**: agent proposes tasks for itself; verifier checks solvability and scores novelty
- **Hidden state**: “held-out” task families for generalization
- **Actions**: generate task, attempt solve, critique, mutate difficulty
- **Reward**:
  - task quality: novelty + non-triviality + solvability
  - learning: improvement on held-out distribution over time
- **Anti-gaming**: penalize trivial tasks, repetitive patterns, or unverifiable tasks

