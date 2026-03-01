<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { onMount } from 'svelte';

	type Suit = 'C' | 'D' | 'H' | 'S' | 'X';
	type Card = [number, Suit];
	type Phase = 'sell' | 'bid' | 'choose' | 'showdown';
	type Objective = 'ev' | 'first_place' | 'robustness';
	type OutputMode = 'action_first' | 'top3' | 'metrics' | 'all';
	type PresetKey = 'balanced_default' | 'correlated_table' | 'risk_on_soft_table' | 'house_control';

	const API = 'http://127.0.0.1:8000';

	let phase: Phase = 'bid';
	let objective: Objective = 'ev';
	let outputMode: OutputMode = 'all';
	let strategyTag = '';
	let presetKey: PresetKey = 'balanced_default';
	let seat = 0;
	let sellerIdx = -1;
	let pot = 200;
	let roundNum = 0;
	let nOrbits = 3;
	let stacks: number[] = [160, 160, 160, 160, 160];
	let myCardsText = '7H 8H 9H 4C 4D';
	let auctionCardsText = '10H';
	let knownCardsText = '';
	let status = '';
	let loading = false;
	let championsLoading = false;
	let recommendation: any = null;
	let sessionState: any = null;
	let eventType: 'bid' | 'auction_result' | 'showdown' | 'note' = 'bid';
	let eventSeat = 0;
	let eventSeller = 0;
	let eventAmount = 0;
	let eventWinner = 0;
	let eventNote = '';

	function parseCards(input: string): Card[] {
		const toks = input
			.toUpperCase()
			.split(/\s+/)
			.map((v) => v.trim())
			.filter(Boolean);
		const cards: Card[] = [];
		for (const t of toks) {
			const m = t.match(/^(10|[1-9])([CDHSX])$/);
			if (!m) continue;
			cards.push([Number(m[1]), m[2] as Suit]);
		}
		return cards;
	}

	function modeEntries(modes: Record<string, any> | undefined): [string, any][] {
		return Object.entries(modes ?? {});
	}

	async function loadSession() {
		const res = await fetch(`${API}/session/state`);
		sessionState = await res.json();
		if (!strategyTag) {
			strategyTag = sessionState?.strategy_presets?.balanced_default ?? sessionState?.champions?.ev ?? '';
		}
	}

	function applyPreset() {
		const next = sessionState?.strategy_presets?.[presetKey];
		if (next) strategyTag = next;
	}

	function applyObjectiveChampion() {
		const next = sessionState?.resolved_champions?.[objective] ?? sessionState?.champions?.[objective];
		if (next) strategyTag = next;
	}

	function applyAutoPreset() {
		const key = sessionState?.recommended_preset;
		if (!key) return;
		const next = sessionState?.strategy_presets?.[key];
		if (next) strategyTag = next;
	}

	async function recommend() {
		loading = true;
		status = '';
		try {
			const payload = {
				seat,
				phase,
				seller_idx: sellerIdx,
				round_num: roundNum,
				n_orbits: nOrbits,
				pot,
				stacks,
				my_cards: parseCards(myCardsText),
				auction_cards: parseCards(auctionCardsText),
				known_cards: parseCards(knownCardsText),
				objective,
				output_mode: outputMode,
				strategy_tag: strategyTag || null
			};
			const res = await fetch(`${API}/advisor/recommend`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify(payload)
			});
			recommendation = await res.json();
			status = 'Recommendation updated';
		} catch (err) {
			status = `Request failed: ${String(err)}`;
		} finally {
			loading = false;
		}
	}

	async function sendEvent() {
		const payload: any = {
			event_type: eventType,
			seat: eventSeat,
			seller_idx: eventSeller,
			amount: eventAmount,
			winner_idx: eventWinner,
			note: eventNote || null
		};
		await fetch(`${API}/session/event`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify(payload)
		});
		eventNote = '';
		await loadSession();
		status = 'Event logged';
	}

	async function recomputeChampions() {
		championsLoading = true;
		status = '';
		try {
			await fetch(`${API}/strategies/recompute_champions`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ n_matches: 60, n_games_per_match: 10, seed: Date.now() % 100000 })
			});
			await loadSession();
			status = 'Champions recomputed';
		} catch (err) {
			status = `Champion run failed: ${String(err)}`;
		} finally {
			championsLoading = false;
		}
	}

	function setStack(i: number, value: string) {
		const n = Number(value);
		stacks[i] = Number.isFinite(n) ? Math.max(0, n) : 0;
		stacks = [...stacks];
	}

	onMount(loadSession);
</script>

<main class="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-4 p-4">
	<header class="rounded-none border bg-[linear-gradient(130deg,#f8f4e8,#fff,#e7f3ff)] p-4">
		<h1 class="text-xl font-semibold tracking-tight">Sold 'Em live HUD advisor</h1>
		<p class="mt-1 text-sm text-muted-foreground">
			Fast state entry, objective-aware recommendations, and profile tracking under a 10-second turn budget.
		</p>
	</header>

	<div class="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
		<section class="space-y-4">
			<div class="rounded-none border bg-card p-3">
				<div class="mb-2 text-sm font-medium">Round state input</div>
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="text-sm">Phase
						<select class="mt-1 h-9 w-full border bg-background px-2" bind:value={phase}>
							<option value="sell">sell</option>
							<option value="bid">bid</option>
							<option value="choose">choose</option>
							<option value="showdown">showdown</option>
						</select>
					</label>
					<label class="text-sm">Objective
						<select class="mt-1 h-9 w-full border bg-background px-2" bind:value={objective}>
							<option value="ev">ev</option>
							<option value="first_place">first_place</option>
							<option value="robustness">robustness</option>
						</select>
					</label>
					<label class="text-sm">Output mode
						<select class="mt-1 h-9 w-full border bg-background px-2" bind:value={outputMode}>
							<option value="action_first">action_first</option>
							<option value="top3">top3</option>
							<option value="metrics">metrics</option>
							<option value="all">all</option>
						</select>
					</label>
					<label class="text-sm">Your seat
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="0" max="4" bind:value={seat} />
					</label>
					<label class="text-sm">Seller seat
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="-1" max="4" bind:value={sellerIdx} />
					</label>
					<label class="text-sm">Pot
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="0" bind:value={pot} />
					</label>
					<label class="text-sm">Round num
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="0" bind:value={roundNum} />
					</label>
					<label class="text-sm">Orbits
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="1" bind:value={nOrbits} />
					</label>
					<label class="text-sm">Strategy tag (optional)
						<input class="mt-1 h-9 w-full border bg-background px-2" placeholder="adaptive_profile" bind:value={strategyTag} />
					</label>
				</div>
					<div class="mt-2 grid gap-2 sm:grid-cols-[1fr_auto_auto]">
					<label class="text-sm">Quick preset
						<select class="mt-1 h-9 w-full border bg-background px-2" bind:value={presetKey}>
							<option value="balanced_default">balanced_default</option>
							<option value="correlated_table">correlated_table</option>
							<option value="risk_on_soft_table">risk_on_soft_table</option>
							<option value="house_control">house_control</option>
						</select>
					</label>
						<Button class="mt-6 rounded-none" variant="outline" onclick={applyPreset}>Use preset</Button>
						<Button class="mt-6 rounded-none" variant="outline" onclick={applyObjectiveChampion}>Use objective champion</Button>
					</div>
					<div class="mt-2">
						<Button class="rounded-none" variant="outline" onclick={applyAutoPreset}>Use auto table read preset</Button>
					</div>

				<div class="mt-3 grid gap-2 sm:grid-cols-3">
					<div class="text-sm">
						<div>My cards</div>
						<input class="mt-1 h-9 w-full border bg-background px-2" bind:value={myCardsText} />
					</div>
					<div class="text-sm">
						<div>Auction cards</div>
						<input class="mt-1 h-9 w-full border bg-background px-2" bind:value={auctionCardsText} />
					</div>
					<div class="text-sm">
						<div>Known cards</div>
						<input class="mt-1 h-9 w-full border bg-background px-2" bind:value={knownCardsText} />
					</div>
				</div>

				<div class="mt-3">
					<div class="mb-1 text-sm">Stacks (P0-P4)</div>
					<div class="grid grid-cols-5 gap-2">
						{#each stacks as stack, i}
							<input
								class="h-9 w-full border bg-background px-2 text-sm"
								type="number"
								value={stack}
								oninput={(e) => setStack(i, (e.target as HTMLInputElement).value)}
							/>
						{/each}
					</div>
				</div>

				<div class="mt-3 flex flex-wrap gap-2">
					<Button class="rounded-none" onclick={recommend} disabled={loading}>
						{loading ? 'Thinking...' : 'Get recommendation'}
					</Button>
					<Button class="rounded-none" variant="outline" onclick={loadSession}>Refresh session</Button>
					<Button class="rounded-none" variant="outline" onclick={recomputeChampions} disabled={championsLoading}>
						{championsLoading ? 'Running...' : 'Recompute champions'}
					</Button>
				</div>
			</div>

			<div class="rounded-none border bg-card p-3">
				<div class="mb-2 text-sm font-medium">Advisor output</div>
				{#if recommendation}
					{#if recommendation.modes}
						<div class="grid gap-2 md:grid-cols-3">
							{#each modeEntries(recommendation.modes) as [mode, rec]}
								<div class="border p-2 text-sm">
									<div class="font-medium">{mode}</div>
									<div class="mt-1">Primary: {JSON.stringify(rec.primary_action)}</div>
									<div class="mt-1 text-xs text-muted-foreground">{rec.rationale}</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="text-sm">Primary: {JSON.stringify(recommendation.primary_action)}</div>
						<div class="mt-2 text-sm">Top actions:</div>
						<div class="mt-1 flex flex-wrap gap-2">
							{#each recommendation.top_actions ?? [] as a}
								<div class="border px-2 py-1 text-xs">{JSON.stringify(a)}</div>
							{/each}
						</div>
						<div class="mt-2 text-xs text-muted-foreground">{recommendation.rationale}</div>
					{/if}
				{:else}
					<div class="text-sm text-muted-foreground">No recommendation yet.</div>
				{/if}
			</div>
		</section>

		<aside class="space-y-4">
				<div class="rounded-none border bg-card p-3">
					<div class="mb-2 text-sm font-medium">Session tracking</div>
					<div class="grid gap-2 sm:grid-cols-2">
					<label class="text-sm">Event
						<select class="mt-1 h-9 w-full border bg-background px-2" bind:value={eventType}>
							<option value="bid">bid</option>
							<option value="auction_result">auction_result</option>
							<option value="showdown">showdown</option>
							<option value="note">note</option>
						</select>
					</label>
						<label class="text-sm">Seat
							<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="0" max="4" bind:value={eventSeat} />
						</label>
						<label class="text-sm">Seller
							<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="-1" max="4" bind:value={eventSeller} />
						</label>
						<label class="text-sm">Amount
							<input class="mt-1 h-9 w-full border bg-background px-2" type="number" bind:value={eventAmount} />
						</label>
					<label class="text-sm">Winner
						<input class="mt-1 h-9 w-full border bg-background px-2" type="number" min="0" max="4" bind:value={eventWinner} />
					</label>
				</div>
				<label class="mt-2 block text-sm">Note
					<input class="mt-1 h-9 w-full border bg-background px-2" bind:value={eventNote} />
				</label>
				<div class="mt-3 flex gap-2">
					<Button class="rounded-none" onclick={sendEvent}>Log event</Button>
					<Button class="rounded-none" variant="outline" onclick={() => fetch(`${API}/session/reset`, { method: 'POST' }).then(loadSession)}>
						Reset session
					</Button>
				</div>
				{#if status}
					<div class="mt-2 text-xs text-muted-foreground">{status}</div>
				{/if}
			</div>

			<div class="rounded-none border bg-card p-3">
				<div class="mb-2 text-sm font-medium">Champions and profiles</div>
				{#if sessionState}
					<div class="text-xs">Rule profile: {sessionState.rule_profile?.name}</div>
					<div class="mt-2 text-xs">Champions: {JSON.stringify(sessionState.champions)}</div>
					<div class="mt-2 text-xs">Resolved champions: {JSON.stringify(sessionState.resolved_champions)}</div>
					<div class="mt-2 text-xs">Table read: {JSON.stringify(sessionState.table_read)}</div>
					<div class="mt-2 text-xs">Recommended preset: {sessionState.recommended_preset}</div>
					<div class="mt-2 text-xs">Strategy presets: {JSON.stringify(sessionState.strategy_presets)}</div>
					<div class="mt-2 text-xs">Composite presets: {JSON.stringify(sessionState.composite_profiles)}</div>
					<div class="mt-2 max-h-60 overflow-y-auto text-xs">
						{#each Object.entries(sessionState.player_profiles ?? {}) as [seatId, profile]}
							<div class="border-b py-1">P{seatId}: {JSON.stringify(profile)}</div>
						{/each}
					</div>
				{:else}
					<div class="text-sm text-muted-foreground">Loading...</div>
				{/if}
			</div>
		</aside>
	</div>

	<footer class="rounded-none border p-3 text-xs text-muted-foreground">
		Card format: `value+suit`, for example `10X 7H 4D`. Suits are `C D H S X`.
		{#if recommendation && recommendation.primary_action?.amount !== undefined}
			Last suggested bid: {recommendation.primary_action.amount}
		{/if}
	</footer>
</main>
