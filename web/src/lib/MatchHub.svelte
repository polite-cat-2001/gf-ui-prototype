<script>
  import { onMount } from 'svelte'
  import Glyph from './Glyph.svelte'
  import { api } from './api.js'

  let { teams, onback } = $props()

  const ACTIONS = [
    { id: 'play', label: 'Выход на поле', glyph: 'pitch' },
    { id: 'manage', label: 'Руководство командой', glyph: 'tactics' },
    { id: 'match', label: 'Параметры игры', glyph: 'sliders' },
    { id: 'sides', label: 'Выб. стороны', glyph: 'sides' },
  ]

  const ROLE_LABEL = {
    GK: 'ВР',
    CB: 'ЦЗ',
    LB: 'ЛЗ',
    RB: 'ПЗ',
    DM: 'ОП',
    CM: 'ЦП',
    LM: 'ЛФ',
    RM: 'ПФ',
    AM: 'АП',
    CF: 'ЦФ',
  }

  const LINE_ORDER = { GK: 0, LB: 1, CB: 2, RB: 3, DM: 4, CM: 5, AM: 6, LM: 7, RM: 8, CF: 9 }

  let selected = $state(0)
  let loading = $state(true)
  let squads = $state({ home: [], away: [] })
  let ratings = $state({ home: null, away: null })

  const metaLine = $derived.by(() => {
    if (!teams) return 'Товарищеский матч'
    if (teams.home?.kind === 'national' && teams.away?.kind === 'national') return 'Сборные'
    return teams.home?.league && teams.home.league === teams.away?.league
      ? teams.home.league
      : 'Товарищеский матч'
  })

  const captainHome = $derived(captainOf(squads.home))
  const captainAway = $derived(captainOf(squads.away))

  function captainOf(rows) {
    return rows.reduce((best, player) => (!best || player.overall > best.overall ? player : best), null)?.id
  }

  function bestEleven(rows) {
    const used = new Set()
    const take = (roles, count) => {
      const picked = rows
        .filter((player) => roles.includes(player.role) && !used.has(player.id))
        .sort((a, b) => b.overall - a.overall)
        .slice(0, count)
      picked.forEach((player) => used.add(player.id))
      return picked
    }

    const lineup = [
      ...take(['GK'], 1),
      ...take(['CB'], 2),
      ...take(['LB'], 1),
      ...take(['RB'], 1),
      ...take(['DM'], 1),
      ...take(['CM', 'AM'], 2),
      ...take(['CF'], 1),
      ...take(['LM', 'RM'], 2),
    ]
    const rest = rows
      .filter((player) => !used.has(player.id))
      .sort((a, b) => b.overall - a.overall)
    lineup.push(...rest.slice(0, Math.max(0, 11 - lineup.length)))

    return lineup.sort(
      (a, b) =>
        (LINE_ORDER[a.role] ?? 9) - (LINE_ORDER[b.role] ?? 9) ||
        b.overall - a.overall,
    )
  }

  function displayName(player, rows) {
    const last = player.last_name || player.name
    const duplicates = rows.filter((item) => (item.last_name || item.name) === last).length
    return duplicates > 1 && player.first_name ? `${player.first_name[0]}. ${last}` : last
  }

  async function loadSquad(team) {
    if (!team?.id) return []
    const rows =
      team.kind === 'national' ? await api.nationalSquad(team.id) : await api.squad(team.id)
    return bestEleven(rows)
  }

  async function loadRating(team) {
    if (team?.rating) return team.rating
    if (!team?.id || team.kind === 'national') return null
    try {
      return await api.clubRatings(team.id)
    } catch {
      return null
    }
  }

  onMount(async () => {
    const [home, away, homeRating, awayRating] = await Promise.all([
      loadSquad(teams.home).catch(() => []),
      loadSquad(teams.away).catch(() => []),
      loadRating(teams.home),
      loadRating(teams.away),
    ])
    squads = { home, away }
    ratings = { home: homeRating, away: awayRating }
    loading = false
  })

  export function input(deviceId, action) {
    if (action === 'back') {
      onback?.()
      return
    }
    if (action === 'left') selected = Math.max(0, selected - 1)
    else if (action === 'right') selected = Math.min(ACTIONS.length - 1, selected + 1)
  }
</script>

{#snippet lineupColumn(rows, captainId, side)}
  <aside class="lineup lineup--{side}">
    <ol class="lineup__list">
      {#if loading}
        <li class="lineup__empty">Загрузка состава…</li>
      {:else if rows.length}
        {#each rows as player, index (player.id)}
          <li class="lineup__row" class:is-gk={player.role === 'GK'}>
            <span class="lineup__num">{player.shirt_number ?? index + 1}</span>
            <span class="lineup__name" title={player.name}>{displayName(player, rows)}</span>
            {#if player.id === captainId}<span class="lineup__cap">К</span>{/if}
            <span class="lineup__role">{ROLE_LABEL[player.role] ?? player.role}</span>
          </li>
        {/each}
      {:else}
        <li class="lineup__empty">Состав недоступен</li>
      {/if}
    </ol>
  </aside>
{/snippet}

<div class="hub">
  <div class="hub__top">
    {@render lineupColumn(squads.home, captainHome, 'home')}

    <section class="scoreboard">
      <div class="scoreboard__meta">
        <span>{metaLine}</span>
        <strong>Новичок · 6 мин · Закат</strong>
      </div>

      <div class="scoreboard__clubs">
        {#each ['home', 'away'] as side (side)}
          {@const team = teams[side]}
          {@const rating = ratings[side]}
          {@const stars = rating?.stars ?? 0}
          <article class="scoreboard__club">
            <span class="hub__venue">{side === 'home' ? 'Дома' : 'Гости'}</span>
            <h2 class="hub__name">{team?.name ?? '—'}</h2>
            <div class="hub__crest">
              {#if team?.logo}<img src={team.logo} alt="" />{/if}
            </div>
            <span class="team__stars">
              {#each Array.from({ length: 5 }, (_, index) => index) as index (index)}
                <span
                  class="team__star"
                  class:team__star--full={stars >= index + 1}
                  class:team__star--half={stars > index && stars < index + 1}
                >★</span>
              {/each}
            </span>
            <div class="team__stats">
              <span class="team__stat"><em>Нап</em><b>{rating?.attack ?? '—'}</b></span>
              <span class="team__stat"><em>Пзщ</em><b>{rating?.midfield ?? '—'}</b></span>
              <span class="team__stat"><em>Защ</em><b>{rating?.defence ?? '—'}</b></span>
            </div>
          </article>
        {/each}
      </div>
    </section>

    {@render lineupColumn(squads.away, captainAway, 'away')}
  </div>

  <div class="command">
    {#each ACTIONS as action, index (action.id)}
      <button
        type="button"
        class="command__cell"
        class:is-selected={index === selected}
        onmouseenter={() => (selected = index)}
        onclick={() => (selected = index)}
      >
        <span class="command__label">{action.label}</span>
        <span class="command__glyph"><Glyph name={action.glyph} size={40} /></span>
      </button>
    {/each}
  </div>
</div>
