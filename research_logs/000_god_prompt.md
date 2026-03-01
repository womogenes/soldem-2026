# PROMPT

## Goal

## You are a highly experienced quantitative trading researcher and engineer. Run experiments to discover the best possible strategy for Sold 'Em and integrate it into a HUD for the game tomorrow happening at 7 am PST. You have this entire time to experiment and figure out the best strategy; it is important that you log out the time as you work. During compaction, reference this document 000_god_prompt.md so that future rollouts know the spec.

## Approach

- Read the rules (in RULES.md) and the implementation of the game in game/engine_base.py. [RULES.md](http://RULES.md) is the source of truth and takes precedence over any existing code. For example, the rankings in [utils.py](http://utils.py) could be totally wrong. You should do the math and recalculate these.
- Do extensive research on the literature of auctioning games, playing against humans, imperfect information games, poker, etc. and put it in a local Markdown file.
- From here, the strategy is roughly:
  - Figure out a common format for strategies (Python files?) so that a single strategy can have its own unique tag and you can simply reference five Python files to evaluate them against each other for some number (1k?) of rollouts to collect data. It is imperative that you do not use a verbose format for logging game history. Text files are likely preferred, though you may edit this later if it proves inefficient. Git commit this.
  - Come up with a centralized database (prefer pocketbase) where strategies are stored and note their implementation, weaknesses, etc. Put this on an AWS instance (CLI usage described below)
  - The idea is to have a set of diverse strategies and develop new strategies that can successfully exploit them. Keep in mind that correlation dynamics may be important to take into account here, as we are playing against humans, not Nash equilibria. The core of this is a bootstrapping process where we continually get better and less exploitable strategies. Beware of staleness though: early strategies might be good at exploiting later strategies simply because we haven’t run them against each other in a long time. Test a wide variety.
  - To do this, you will need to first have a good framework for running different strategies against each other.
  - It may be helpful to spawn new Codex instances to work separately in different worktrees, or on EC2 instances, to come up with brand new ideas. Seed them well from your research, or direct them to conduct new research, and have them update the database or ping you (set up a system for this and test it with some dummy systems) as they do. Ensure these instances have context and develop novel ideas. If you do this, you should check the database frequently.

You have a LOT of latitude in this process. Explore new goals as you see fit. Prioritize creative research. You are also welcome to spawn new agents to work on random research and explore new ideas. At the end of the day, we want a website that will help us win the competition. Whether this ends up being a HUD or something that reports statistics with instructions is up to you. However, to be useful, we should be able to input game state quickly (i.e. less clutter) and get the information we need in an intuitive manner. In service of this, it may be helpful to scrap all of web/ and restart from scratch. It’s in the git history anyway.

We are playing \~10 games against humans, though conduct the same research on what happens if we play more or fewer games. It may be useful to test variations as well, as mentioned in the rules (see note at end). There will be rule variations that are not mentioned until day-of; write a .md document for a future agent that will run day-of that instructs it on how to patch the system, given new rule variations. This new agent should be able to patch the whole system in under 2 minutes. It may be helpful to precompute different possible variations (some ideas are mentioned at the end of this doc). Take into account really weird possibilities.

### Notes about approach

- You have access to the codex CLI locally, in addition to Amazon Bedrock (use for LMPs, i.e. language model programs). Use it to your advantage where applicable.
- Derisk experiments by running them on small scale before doing time-consuming tasks. Remember, you only have until 7 am PT. Use these 6-7 hours wisely. If ever I ask you to "keep working," there are almost certainly improvements to be had or totally novel ideas to be explored.
- You have access to AWS CLI and are welcome to spin up as many EC2 instances as you want to run parallel workers, jobs, simulations, Codex instances, etc. Don’t spend more than $10k though, and ensure you plan and design systems well.
- Use uv for Python dependency management.

## To get LLM API access

You have access to the AWS CLI locally. Set up Amazon Bedrock. See [https://code.claude.com/docs/en/amazon-bedrock](https://code.claude.com/docs/en/amazon-bedrock). Use this to set up LMPs (language model programs) if needed for various agents, whether for trading or as part of API access for substrategies. You are allowed to install Codex on these remote servers and copy over your local keys to auth it. Use these remote Codex instances to explore strategies independently (as discussed earlier).

You have a (passphrase-free) ssh key in \~/.codex/.ssh/id_ed25519.pub. Use it to make commits, push to github, make worktrees, etc. that the separate Codex instances can clone.

## Conditions

Do not stop working until 7 am PT. Right before 7 am PT, write a summary doc that explains what we have and how to use it. Web UI should be fully up and running.

## Notes

- It's possible that there are bad externalities. For example, two players might "really respect each other" and correlate in ways that are bad for everyone else. When running simulations, it's important to simulate this kind of correlation.
- Write logs in research_logs/ as you work. Include local timestamps at the top so that in retrospect we have a good timeline.
- Generally, test stuff end-to-end.

## Some basic strategies (roughly)

These are just for inspiration. You should absolutely brainstorm your own ideas off the research you collect.

- Calculate P(win given win auction) \- P(win given lose auction) as delta P. delta P \* pot tells us the "fair value" for this card. Notably, this is not the same as how much we should bid due to various factors (e.g. adversity from winning the auction, etc.). In fact, P(win given win auction) should be conditioned on bid size as this is a key factor.
- We are playing against humans. During inference, it may be a beneficial strategy to keep profiles of players (their history) and take this into account during the game.
- Note that if we are able to sell cards and make 40 chips per round, this breaks us even. If we make 60 chips per round selling our own cards (note we can only sell three times), we net 20 profit. Steadily getting 20 chips profit each time seems like a reasonable strategy, though people may try to exploit this.
- It would be helpful to explore a strategy that _just_ uses LLMs (e.g. Opus 4.6), though keep in mind the 10 second latency requirement.
- Since players are likely to stay the same between at least a few rounds (and possibly many), it may be worthwhile to explore building profiles on players or exploiting dynamics between players. Social effects are real and must be accounted for. It will be the case that we see players’ cards during showdown and can reinforce our strategy according to that.
- Tracking info on who has what cards (as a result of trading OR as a result of unbought cards going back to players) may be relevant.

Some more thoughts

- What do we hope to want after this finishes
  - We want a system that can train a human. This may be by having a robust set of strategies for the human to learn by playing against, or critical takeaways from analysis from key heuristics learned from developing stronger strategies through whatever means necessary
  - We also want a system that can assist the human the day of: this system should be able to easily inject the data necessary for it, and then communicate important information to the human player in order for the player to better execute this strategy. Depending on your findings, this may take the form of a few metrics and numbers about suggested bet sizes and insights that the human player can refer to and make a holistic decision, or this could be of the form of a cohesive strategy that takes in the game state and history and any other relevant information and outputs the exact strategy the human player should follow. At the end of the day, the goal of this project and this system and this research is to do well on this competition. If your findings lead you to conclude that certain parts of human intuition are necessary, then training the human and providing key metrics may be the best approach. Alternatively, if you are able to build a system that is demonstrably superhuman and will perform robustly against real world conditions and adapt to information and do all the key tasks needed to win the competition on its own, then you should build that. Thinking critically about how these systems should behave is also part of your job \- feel free to implement multiple options/alternatives.
- One specific research direction that is viable
  - An approach for this research is to do some sort of evolutionary strategy search. It may be that more traditional approaches (e.g. cfr, rl) are not suited well for this multiparty domain, are too slow, or do not do super well in practice against off-nash humans where other strategies may perform a lot better. Under this regime, the following approach may be better suited. \[this is described above\]. Keep in mind that the ultimate goal is to have a system that does well in practice in this competition against a diverse set of reasonable human opponents.
