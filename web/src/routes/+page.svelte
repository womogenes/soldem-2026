<script lang="ts">
	import { onMount } from 'svelte';

	type Suit = 'C' | 'D' | 'H' | 'S' | 'X';
	type Card = [number, Suit];
	type Phase = 'sell' | 'bid' | 'choose' | 'showdown';
	type Objective = 'ev' | 'first_place' | 'robustness';

	const API = import.meta.env.VITE_API_BASE ?? '/api';

	let objective: Objective = 'ev';
	let phase: Phase = 'bid';
	let seat = 0;
	let sellerIdx = -1;
	let pot = 200;
	let roundNum = 0;
	let nOrbits = 3;
	let stacksText = '160 160 160 160 160';
	let myCardsText = '7H 8H 9H 4C 4D';
	let auctionCardsText = '10H';
	let intelBySeatText = '1: 8H 9H; 3: 10C';
	let strategyOverride = '';
	let useAutoStrategy = true;
	let sessionState: any = null;
	let recommendation: any = null;
	let loading = false;
	let status = '';

	function parseCards(input: string): Card[] {
		const tokens = input
			.toUpperCase()
			.split(/[,\s]+/)
			.map((v) => v.trim())
			.filter(Boolean);
		const cards: Card[] = [];
		for (const token of tokens) {
			const match = token.match(/^(10|[1-9])([CDHSX])$/);
			if (!match) continue;
			cards.push([Number(match[1]), match[2] as Suit]);
		}
		return cards;
	}

	function parseStacks(input: string): number[] {
		const raw = input
			.split(/[,\s]+/)
			.map((v) => Number(v))
			.filter((v) => Number.isFinite(v))
			.map((v) => Math.max(0, Math.round(v)));
		const stacks = raw.slice(0, 5);
		while (stacks.length < 5) stacks.push(160);
		return stacks;
	}

	function parseIntelBySeat(input: string): Record<number, Card[]> {
		const out: Record<number, Card[]> = {};
		const chunks = input
			.split(';')
			.map((v) => v.trim())
			.filter(Boolean);
		for (const chunk of chunks) {
			const parts = chunk.split(':');
			if (parts.length < 2) continue;
			const seat = Number(parts[0].trim());
			if (!Number.isFinite(seat) || seat < 0 || seat > 4) continue;
			const cards = parseCards(parts.slice(1).join(':'));
			if (cards.length) out[seat] = cards;
		}
		return out;
	}

	function mergeIntelBySeat(
		base: Record<number, Card[]>,
		overlay: Record<number, Card[]>
	): Record<number, Card[]> {
		const out: Record<number, Card[]> = {};
		for (const [rawSeat, cards] of Object.entries(base)) {
			const seat = Number(rawSeat);
			if (!Number.isFinite(seat)) continue;
			out[seat] = [...cards];
		}
		for (const [rawSeat, cards] of Object.entries(overlay)) {
			const seat = Number(rawSeat);
			if (!Number.isFinite(seat)) continue;
			const seen = new Set((out[seat] ?? []).map((c) => `${c[0]}${c[1]}`));
			const merged = [...(out[seat] ?? [])];
			for (const card of cards) {
				const key = `${card[0]}${card[1]}`;
				if (seen.has(key)) continue;
				seen.add(key);
				merged.push(card);
			}
			out[seat] = merged;
		}
		return out;
	}

	function defaultStrategyFor(state: any, obj: Objective): string {
		return state?.policy_map?.default?.[obj] ?? state?.champions?.[obj] ?? '';
	}

	function alternatesFor(state: any, obj: Objective): string[] {
		const row = state?.policy_map?.alternates?.[obj];
		return Array.isArray(row) ? row : [];
	}

	$: defaultStrategy = defaultStrategyFor(sessionState, objective);
	$: alternateStrategies = alternatesFor(sessionState, objective);
	$: activeStrategy = useAutoStrategy ? defaultStrategy : strategyOverride.trim();

	$: output = recommendation?.modes?.action_first ?? recommendation;
	$: primaryAction = output?.primary_action ?? {};
	$: primaryType = String(primaryAction?.type ?? 'hold').toUpperCase();
	$: primaryAmount = primaryAction?.amount;

	function setAlternate(tag: string) {
		strategyOverride = tag;
		useAutoStrategy = false;
		status = `Override active: ${tag}`;
	}

	async function loadSession() {
		try {
			const res = await fetch(`${API}/session/state`);
			sessionState = await res.json();
			if (useAutoStrategy && defaultStrategyFor(sessionState, objective)) {
				strategyOverride = '';
			}
		} catch (err) {
			status = `Session load failed: ${String(err)}`;
		}
	}

	async function runCall() {
		loading = true;
		status = '';
		try {
			const textIntel = parseIntelBySeat(intelBySeatText);
			const sessionIntel = (sessionState?.known_cards_by_seat ?? {}) as Record<number, Card[]>;
			const intelBySeat = mergeIntelBySeat(sessionIntel, textIntel);
			const knownCards = Object.values(intelBySeat).flat();
			const payload = {
				seat,
				phase,
				seller_idx: sellerIdx,
				round_num: roundNum,
				n_orbits: nOrbits,
				pot,
				stacks: parseStacks(stacksText),
				my_cards: parseCards(myCardsText),
				auction_cards: parseCards(auctionCardsText),
				known_cards: knownCards,
				known_cards_by_seat: intelBySeat,
				objective,
				output_mode: 'all',
				strategy_tag: activeStrategy || null,
				auto_policy_condition: true,
				match_horizon: 10
			};
			const res = await fetch(`${API}/advisor/recommend`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify(payload)
			});
			recommendation = await res.json();
			status = 'Call computed';
		} catch (err) {
			status = `Call failed: ${String(err)}`;
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		await loadSession();
		await runCall();
	});
</script>

<svelte:head>
	<title>Sold 'Em command board</title>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<main class="stage">
	<div class="orb orb-1" aria-hidden="true"></div>
	<div class="orb orb-2" aria-hidden="true"></div>

	<section class="panel hero">
		<div class="eyebrow">Live call</div>
		<div class="headline">{primaryType}</div>
		{#if primaryAmount !== undefined}
			<div class="amount">{primaryAmount}</div>
		{/if}
		<div class="hero-meta">
			<span>Objective: {objective}</span>
			<span>Phase: {phase}</span>
			<span>Strategy: <code>{activeStrategy || 'auto'}</code></span>
		</div>
		<div class="hero-actions">
			<button class="btn btn-primary" onclick={runCall} disabled={loading}>
				{loading ? 'Computing...' : 'Recompute now'}
			</button>
			<button class="btn" onclick={loadSession}>Refresh state</button>
		</div>
		{#if status}
			<div class="status">{status}</div>
		{/if}
	</section>

	<section class="grid">
		<article class="panel block reveal-1">
			<h2>Decision switches</h2>
			<div class="field-row">
				<label>Objective
					<select bind:value={objective}>
						<option value="ev">ev</option>
						<option value="first_place">first_place</option>
						<option value="robustness">robustness</option>
					</select>
				</label>
				<label>Phase
					<select bind:value={phase}>
						<option value="sell">sell</option>
						<option value="bid">bid</option>
						<option value="choose">choose</option>
						<option value="showdown">showdown</option>
					</select>
				</label>
			</div>
			<div class="field-row">
				<label>Seat
					<input type="number" min="0" max="4" bind:value={seat} />
				</label>
				<label>Seller
					<input type="number" min="-1" max="4" bind:value={sellerIdx} />
				</label>
				<label>Pot
					<input type="number" min="0" bind:value={pot} />
				</label>
			</div>
			<div class="field-row">
				<label>Round
					<input type="number" min="0" bind:value={roundNum} />
				</label>
				<label>Orbits
					<input type="number" min="1" bind:value={nOrbits} />
				</label>
			</div>
		</article>

		<article class="panel block reveal-2">
			<h2>Table input</h2>
			<label>My cards
				<input bind:value={myCardsText} placeholder="7H 8H 9H 4C 4D" />
			</label>
			<label>Auction cards
				<input bind:value={auctionCardsText} placeholder="10H" />
			</label>
			<label>Stacks (P0 P1 P2 P3 P4)
				<input bind:value={stacksText} placeholder="160 160 160 160 160" />
			</label>
			<label>Opponent intel by seat
				<input bind:value={intelBySeatText} placeholder="1: 8H 9H; 3: 10C 10D" />
			</label>
		</article>

		<article class="panel block reveal-3">
			<h2>Strategy rail</h2>
			<div class="mini">
				<div>Default</div>
				<code>{defaultStrategy || 'n/a'}</code>
			</div>
			<div class="mini">
				<label class="toggle">
					<input
						type="checkbox"
						bind:checked={useAutoStrategy}
						onchange={() => {
							if (useAutoStrategy) strategyOverride = '';
						}}
					/>
					<span>Auto strategy</span>
				</label>
			</div>
			<label>Manual override
				<input
					bind:value={strategyOverride}
					oninput={() => {
						if (strategyOverride.trim()) useAutoStrategy = false;
					}}
					placeholder="seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2"
				/>
			</label>
			{#if alternateStrategies.length}
				<div class="chips">
					{#each alternateStrategies as alt}
						<button class="chip" type="button" onclick={() => setAlternate(alt)}>{alt}</button>
					{/each}
				</div>
			{/if}
		</article>

		<article class="panel block reveal-4">
			<h2>Signal feed</h2>
			<div class="mini"><div>Correlation</div><code>{recommendation?.inferred_correlation?.mode ?? 'n/a'}</code></div>
			<div class="mini"><div>Condition key</div><code>{recommendation?.selected_condition_key ?? 'n/a'}</code></div>
			<div class="mini"><div>Known card count</div><code>{output?.metrics?.known_cards_count ?? 0}</code></div>
			<div class="mini"><div>Rationale</div><p>{output?.rationale ?? 'No rationale yet.'}</p></div>
			{#if output?.top_actions?.length}
				<div class="mini">
					<div>Top actions</div>
					<pre>{JSON.stringify(output.top_actions, null, 2)}</pre>
				</div>
			{/if}
		</article>
	</section>
</main>

<style>
	:global(body) {
		font-family: 'Space Grotesk', 'Trebuchet MS', sans-serif;
	}

	.stage {
		position: relative;
		min-height: 100vh;
		padding: 2.4rem 1rem 3rem;
		background:
			radial-gradient(1200px 700px at 15% -10%, rgba(255, 202, 140, 0.5), transparent 65%),
			radial-gradient(900px 600px at 90% 0%, rgba(106, 173, 255, 0.45), transparent 62%),
			linear-gradient(180deg, #f9f5ee 0%, #f3f7fb 55%, #eef3f7 100%);
		color: #112235;
	}

	.orb {
		position: absolute;
		border-radius: 999px;
		filter: blur(28px);
		pointer-events: none;
		animation: drift 12s ease-in-out infinite;
	}

	.orb-1 {
		width: 210px;
		height: 210px;
		top: 8%;
		right: 7%;
		background: rgba(255, 156, 84, 0.2);
	}

	.orb-2 {
		width: 260px;
		height: 260px;
		left: -40px;
		bottom: 8%;
		background: rgba(92, 160, 245, 0.22);
		animation-delay: -6s;
	}

	.panel {
		position: relative;
		z-index: 1;
		border: 1px solid rgba(17, 34, 53, 0.16);
		background: rgba(255, 255, 255, 0.76);
		backdrop-filter: blur(8px);
	}

	.hero {
		max-width: 1100px;
		margin: 0 auto 1.25rem;
		padding: 1.2rem 1.2rem 1.35rem;
		animation: lift-in 420ms ease-out;
	}

	.eyebrow {
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.16em;
		font-weight: 700;
		color: #295a83;
	}

	.headline {
		margin-top: 0.4rem;
		font-size: clamp(2rem, 4.5vw, 3.6rem);
		font-weight: 700;
		letter-spacing: 0.02em;
		line-height: 0.92;
	}

	.amount {
		font-family: 'IBM Plex Mono', 'Consolas', monospace;
		font-size: clamp(1.9rem, 5vw, 3.1rem);
		margin-top: 0.15rem;
		font-weight: 600;
		color: #0f4d7f;
	}

	.hero-meta {
		margin-top: 0.65rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		font-size: 0.86rem;
	}

	.hero-meta span {
		border: 1px solid rgba(17, 34, 53, 0.2);
		padding: 0.24rem 0.5rem;
		background: rgba(255, 255, 255, 0.65);
	}

	.hero-meta code,
	code,
	pre {
		font-family: 'IBM Plex Mono', 'Consolas', monospace;
	}

	.hero-actions {
		margin-top: 0.75rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.55rem;
	}

	.btn {
		padding: 0.48rem 0.82rem;
		border: 1px solid rgba(17, 34, 53, 0.35);
		background: rgba(255, 255, 255, 0.78);
		font-weight: 600;
		font-size: 0.85rem;
		cursor: pointer;
		transition: transform 140ms ease, background 140ms ease;
	}

	.btn:hover {
		transform: translateY(-1px);
		background: rgba(246, 251, 255, 0.96);
	}

	.btn-primary {
		background: linear-gradient(135deg, #0f5f9b, #1f7f9e);
		color: #f8fcff;
		border-color: transparent;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: wait;
	}

	.status {
		margin-top: 0.5rem;
		font-size: 0.84rem;
		color: #235678;
	}

	.grid {
		max-width: 1100px;
		margin: 0 auto;
		display: grid;
		gap: 0.8rem;
		grid-template-columns: repeat(12, minmax(0, 1fr));
	}

	.block {
		padding: 0.85rem;
	}

	.block h2 {
		margin: 0 0 0.55rem;
		font-size: 0.95rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.block label {
		display: block;
		font-size: 0.78rem;
		font-weight: 500;
		margin-bottom: 0.55rem;
	}

	.block input,
	.block select {
		display: block;
		margin-top: 0.24rem;
		width: 100%;
		padding: 0.48rem 0.56rem;
		font-size: 0.88rem;
		border: 1px solid rgba(17, 34, 53, 0.25);
		background: rgba(255, 255, 255, 0.87);
	}

	.field-row {
		display: grid;
		gap: 0.5rem;
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}

	.field-row + .field-row {
		margin-top: 0.2rem;
	}

	.mini {
		margin-bottom: 0.55rem;
		padding: 0.5rem;
		border: 1px solid rgba(17, 34, 53, 0.14);
		background: rgba(255, 255, 255, 0.68);
		font-size: 0.78rem;
	}

	.mini p {
		margin: 0.2rem 0 0;
		line-height: 1.4;
	}

	.mini pre {
		margin: 0.25rem 0 0;
		font-size: 0.72rem;
		white-space: pre-wrap;
		word-break: break-word;
	}

	.toggle {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		margin: 0;
	}

	.toggle input {
		width: auto;
		margin: 0;
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.chip {
		border: 1px solid rgba(17, 34, 53, 0.24);
		background: rgba(244, 251, 255, 0.85);
		padding: 0.35rem 0.45rem;
		font-size: 0.7rem;
		cursor: pointer;
	}

	.chip:hover {
		background: rgba(230, 246, 255, 0.95);
	}

	.reveal-1 {
		grid-column: span 6;
		animation: lift-in 350ms ease-out 40ms both;
	}

	.reveal-2 {
		grid-column: span 6;
		animation: lift-in 350ms ease-out 90ms both;
	}

	.reveal-3 {
		grid-column: span 5;
		animation: lift-in 350ms ease-out 140ms both;
	}

	.reveal-4 {
		grid-column: span 7;
		animation: lift-in 350ms ease-out 190ms both;
	}

	@keyframes lift-in {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes drift {
		0%,
		100% {
			transform: translate(0, 0) scale(1);
		}
		50% {
			transform: translate(12px, -10px) scale(1.04);
		}
	}

	@media (max-width: 960px) {
		.grid {
			grid-template-columns: 1fr;
		}

		.reveal-1,
		.reveal-2,
		.reveal-3,
		.reveal-4 {
			grid-column: span 1;
		}

		.field-row {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 620px) {
		.stage {
			padding: 1rem 0.75rem 2rem;
		}

		.field-row {
			grid-template-columns: 1fr;
		}

		.hero {
			padding: 1rem;
		}
	}
</style>
