<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import {
		Club,
		Diamond,
		Heart,
		Hexagon,
		LoaderCircle,
		Plus,
		Spade,
		X
	} from '@lucide/svelte';
	import { onMount, tick } from 'svelte';

	type Suit = 'C' | 'D' | 'H' | 'S' | 'X';
	type Card = [number, Suit];
	type Phase = 'idle' | 'sell' | 'bid' | 'choose' | 'showdown';

	type State = {
		phase: Phase;
		action: string;
		round_winner: number;
		match_pnl: number[];
		log: string[];
		pot: number;
		round_num: number;
		n_orbits: number;
		seller_idx: number;
		player_cards: Card[][];
		player_stacks: number[];
		auc_cards: Card[];
	};

	const API = 'http://127.0.0.1:8000';
	let state: State = {
		phase: 'idle',
		action: 'Start new game',
		round_winner: -1,
		match_pnl: [0, 0, 0, 0, 0],
		log: [],
		pot: 0,
		round_num: 0,
		n_orbits: 3,
		seller_idx: -1,
		player_cards: [[], [], [], [], []],
		player_stacks: [0, 0, 0, 0, 0],
		auc_cards: []
	};
	let playerBidInput = '0';
	let selectedSellIdx: number[] = [];
	let choosingIdx: number | null = null;
	let bidPending = false;
	let logEl: HTMLDivElement | null = null;

	function suitOf(card: Card): Suit {
		return card[1];
	}

	function labelForSeller() {
		return state.seller_idx === -1 ? 'house' : `P${state.seller_idx}`;
	}

	async function loadState() {
		const next = await (await fetch(`${API}/state`)).json();
		await applyState(next);
	}

	async function startNewGame() {
		const next = await (await fetch(`${API}/new_game`, { method: 'POST' })).json();
		await applyState(next);
		selectedSellIdx = [];
		playerBidInput = '0';
	}

	async function resetGame() {
		const next = await (await fetch(`${API}/reset_game`, { method: 'POST' })).json();
		await applyState(next);
		selectedSellIdx = [];
		playerBidInput = '0';
	}

	async function submitSell() {
		const next = await (
			await fetch(`${API}/sell`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ indices: selectedSellIdx })
			})
		).json();
		await applyState(next);
		selectedSellIdx = [];
	}

	async function submitBid() {
		bidPending = true;
		await new Promise((resolve) => setTimeout(resolve, 500));
		const next = await (
			await fetch(`${API}/bid`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ amount: Number(playerBidInput) || 0 })
			})
		).json();
		await applyState(next);
		bidPending = false;
	}

	async function chooseWonCard(index: number) {
		choosingIdx = index;
		const next = await (
			await fetch(`${API}/choose`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ index })
			})
		).json();
		await applyState(next);
		choosingIdx = null;
	}

	async function applyState(next: State) {
		const prevLen = state.log.length;
		state = next;
		if (state.log.length !== prevLen) {
			await tick();
			if (logEl) logEl.scrollTop = 0;
		}
	}

	function toggleSellIdx(i: number) {
		if (selectedSellIdx.includes(i)) {
			selectedSellIdx = selectedSellIdx.filter((x) => x !== i);
		} else {
			selectedSellIdx = [...selectedSellIdx, i];
		}
	}

	onMount(loadState);
</script>

<main class="mx-auto flex w-full max-w-2xl flex-col gap-4 p-4">
	<div class="flex flex-wrap items-center gap-2">
		<Button class="rounded-none" onclick={startNewGame}>Start new game</Button>
		<Button class="rounded-none" variant="outline" onclick={resetGame}>Reset game</Button>
	</div>

	<div class="grid gap-3 md:grid-cols-[minmax(0,1fr)_12rem]">
		<section class="space-y-3">
			<div class="rounded-none border bg-card p-3">
				<div class="text-sm">Pot ${state.pot} · R{state.round_num + 1}/{state.n_orbits}</div>
			</div>

			<div class="grid grid-cols-5 gap-2">
				{#each state.player_stacks as stack, i}
					<div
						class={`rounded-none border bg-card p-2 text-sm transition-colors ${
							i === state.seller_idx ? 'border-blue-500' : ''
						}`}
					>
						P{i} ${stack}
						{#if i === state.round_winner}*{/if}
					</div>
				{/each}
			</div>

			<div class="rounded-none border bg-card p-3">
				<div class="mb-2 text-sm">Auction · {labelForSeller()}</div>
				<div class="flex flex-wrap gap-2">
					{#each state.auc_cards as card, i}
						<button
							class={`flex animate-in items-center gap-1 rounded-none border px-2 py-1 text-sm transition-colors duration-200 fade-in ${
								state.phase === 'choose'
									? 'cursor-pointer border-blue-500 hover:border-blue-500'
									: ''
							} ${choosingIdx === i ? 'border-blue-500' : ''}`}
							onclick={() => state.phase === 'choose' && chooseWonCard(i)}
						>
							{card[0]}
							{#if suitOf(card) === 'C'}<Club class="size-4" />{/if}
							{#if suitOf(card) === 'D'}<Diamond class="size-4 text-red-600" />{/if}
							{#if suitOf(card) === 'H'}<Heart class="size-4 text-red-600" />{/if}
							{#if suitOf(card) === 'S'}<Spade class="size-4" />{/if}
							{#if suitOf(card) === 'X'}<Hexagon class="size-4 text-blue-600" />{/if}
						</button>
					{/each}
				</div>
			</div>

			<div class="rounded-none border bg-card p-3">
				<div class="mb-2 text-sm">You · {state.action}</div>
				<div class="mb-3 flex flex-wrap gap-2">
					{#each state.player_cards[0] ?? [] as card, i}
						<button
							class={`flex items-center gap-1 rounded-none border px-2 py-1 text-sm transition-colors ${
								selectedSellIdx.includes(i) ? 'border-blue-500' : ''
							} ${state.phase === 'sell' ? 'cursor-pointer' : ''}`}
							onclick={() => state.phase === 'sell' && toggleSellIdx(i)}
							aria-pressed={selectedSellIdx.includes(i)}
						>
							{#if state.phase === 'sell'}
								{#if selectedSellIdx.includes(i)}
									<X class="size-3" />
								{:else}
									<Plus class="size-3" />
								{/if}
							{/if}
							{card[0]}
							{#if suitOf(card) === 'C'}<Club class="size-4" />{/if}
							{#if suitOf(card) === 'D'}<Diamond class="size-4 text-red-600" />{/if}
							{#if suitOf(card) === 'H'}<Heart class="size-4 text-red-600" />{/if}
							{#if suitOf(card) === 'S'}<Spade class="size-4" />{/if}
							{#if suitOf(card) === 'X'}<Hexagon class="size-4 text-blue-600" />{/if}
						</button>
					{/each}
				</div>

				{#if state.phase === 'sell'}
					<Button class="rounded-none" onclick={submitSell}>Sell selected</Button>
				{:else if state.phase === 'bid'}
					<div class="flex flex-wrap items-center gap-2">
						<input
							class="h-9 w-24 rounded-none border bg-background px-2 text-sm"
							type="number"
							min="0"
							max={state.seller_idx === 0 ? 0 : (state.player_stacks[0] ?? 0)}
							disabled={state.seller_idx === 0 || bidPending}
							bind:value={playerBidInput}
						/>
						<Button class="rounded-none" onclick={submitBid} disabled={bidPending}>
							{#if bidPending}
								<LoaderCircle class="size-4 animate-spin" />
								Bid
							{:else}
								Bid
							{/if}
						</Button>
					</div>
				{:else if state.phase === 'showdown'}
					<div class="text-sm">Winner P{state.round_winner} · Match PnL {state.match_pnl[0]}</div>
				{/if}
			</div>
		</section>

		<aside class="w-96 rounded-none border bg-card p-3">
			<div class="mb-2 text-sm">Log</div>
			<div bind:this={logEl} class="flex max-h-[24rem] flex-col gap-1 overflow-y-auto text-sm">
				{#each [...state.log].reverse() as entry}
					<div class="animate-in rounded-none p-1 duration-700 fade-in slide-in-from-top-1">
						{entry}
					</div>
				{/each}
			</div>
		</aside>
	</div>
</main>
