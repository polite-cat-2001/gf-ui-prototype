<script>
  import { onMount } from 'svelte'
  import KitArt from './KitArt.svelte'
  import MatchPreview from './MatchPreview.svelte'
  import { kitLabel, loadKitSpecs } from './kits.js'

  let { teams, devices = [], onback } = $props()

  let sides = $state([
    { id: 'home', kits: [], kitIndex: 0, ready: false },
    { id: 'away', kits: [], kitIndex: 0, ready: false },
  ])
  let activeSide = $state('home')
  let error = $state('')

  const homeDevices = $derived(devices.filter((device) => device.connected && device.side === 'home'))
  const awayDevices = $derived(devices.filter((device) => device.connected && device.side === 'away'))
  const parallel = $derived(homeDevices.length > 0 && awayDevices.length > 0)

  const sideOf = (id) => sides.find((side) => side.id === id)
  const canEdit = (side) => {
    if (side.ready) return false
    if (parallel) return true
    return side.id === 'home' || sideOf('home').ready
  }
  const isLive = (side) => canEdit(side) && (parallel || side.id === activeSide)

  const homeKit = $derived(sideOf('home').kits[sideOf('home').kitIndex] ?? null)
  const awayKit = $derived(sideOf('away').kits[sideOf('away').kitIndex] ?? null)

  function stepKit(side, step, event) {
    event?.stopPropagation()
    if (!canEdit(side) || side.kits.length < 2) return
    activeSide = side.id
    side.kitIndex = (side.kitIndex + step + side.kits.length) % side.kits.length
  }

  function pickKit(side, index, event) {
    event?.stopPropagation()
    if (!canEdit(side) || index === side.kitIndex) return
    activeSide = side.id
    side.kitIndex = index
  }

  function focusSide(side) {
    if (canEdit(side)) activeSide = side.id
  }

  function confirm(side) {
    if (!isLive(side) || !side.kits.length) return
    side.ready = true
    if (!parallel) {
      const other = sideOf(side.id === 'home' ? 'away' : 'home')
      if (!other.ready) activeSide = other.id
    }
  }

  function back() {
    if (!parallel) {
      const home = sideOf('home')
      const away = sideOf('away')
      if (away.ready) {
        away.ready = false
        activeSide = 'away'
        return
      }
      if (home.ready) {
        home.ready = false
        activeSide = 'home'
        return
      }
    }
    onback?.()
  }

  function sideForDevice(deviceId) {
    if (!parallel) return sideOf(activeSide)
    const device = devices.find((item) => item.id === deviceId)
    if (!device) return null
    return device.side === 'home' || device.side === 'away' ? sideOf(device.side) : null
  }

  export function input(deviceId, action) {
    if (action === 'back') {
      back()
      return
    }

    const side = sideForDevice(deviceId)
    if (!side || !isLive(side)) return

    if (action === 'confirm') {
      confirm(side)
      return
    }

    const step = action === 'left' ? -1 : action === 'right' ? 1 : 0
    if (step) stepKit(side, step)
  }

  onMount(async () => {
    try {
      const [home, away] = await Promise.all([
        loadKitSpecs(teams.home.id),
        loadKitSpecs(teams.away.id),
      ])
      sideOf('home').kits = home.kits
      sideOf('away').kits = away.kits
    } catch (caught) {
      error = caught.message
    }
  })
</script>

<div class="kits">
  {#each sides as side (side.id)}
    {@const kits = side.kits}
    {@const kit = kits[side.kitIndex]}
    {@const team = teams?.[side.id]}
    {@const prev = kits.length > 1 ? kits[(side.kitIndex + kits.length - 1) % kits.length] : null}
    {@const next = kits.length > 1 ? kits[(side.kitIndex + 1) % kits.length] : null}
    {@const live = isLive(side)}
    <article
      class="kit-panel"
      class:kit-panel--home={side.id === 'home'}
      class:kit-panel--away={side.id === 'away'}
      class:is-focus={live}
      class:is-ready={side.ready}
      style:grid-area={side.id}
      onmouseenter={() => focusSide(side)}
    >
      <header class="kit-panel__head">
        <span class="kit-panel__team">
          {#if team?.logo}<img src={team.logo} alt="" />{/if}
          <span>{team?.name ?? ''}</span>
        </span>
        <span class="kit-panel__count">{kits.length ? `${side.kitIndex + 1} / ${kits.length}` : '—'}</span>
      </header>

      <h2 class="kit-panel__name">{kitLabel(kit)}</h2>

      <div class="kit-panel__carousel">
        <button
          type="button"
          class="kit-arrow kit-arrow--left"
          class:is-active={live && kits.length > 1}
          disabled={!live || kits.length < 2}
          onclick={(event) => stepKit(side, -1, event)}
          aria-label="Предыдущий комплект"
        ></button>

        <div class="kit-neighbor">
          {#if prev}<KitArt kit={prev} />{/if}
        </div>

        <div class="kit-hero">
          {#if kit}<KitArt kit={kit} />{/if}
        </div>

        <div class="kit-neighbor">
          {#if next}<KitArt kit={next} />{/if}
        </div>

        <button
          type="button"
          class="kit-arrow kit-arrow--right"
          class:is-active={live && kits.length > 1}
          disabled={!live || kits.length < 2}
          onclick={(event) => stepKit(side, 1, event)}
          aria-label="Следующий комплект"
        ></button>
      </div>

      <footer class="kit-panel__foot">
        {#if side.ready}
          <span class="kit-panel__ready">Готов!</span>
        {:else if live && kits.length}
          <span class="kit-dots">
            {#each kits as item, index (item.id)}
              <button
                type="button"
                class="kit-dot"
                class:is-on={index === side.kitIndex}
                onclick={(event) => pickKit(side, index, event)}
                aria-label={kitLabel(item)}
              ></button>
            {/each}
          </span>
        {/if}
      </footer>
    </article>
  {/each}

  <aside class="preview">
    <header class="preview__head">
      <span class="preview__title">Превью матча</span>
      <span class="preview__sub">камера сверху</span>
    </header>
    <div class="preview__pitch">
      <MatchPreview home={homeKit} away={awayKit} />
    </div>
    <footer class="preview__foot">
      <span class="preview__team">{teams?.home?.name ?? ''}</span>
      <span class="preview__vs">vs</span>
      <span class="preview__team">{teams?.away?.name ?? ''}</span>
    </footer>
  </aside>
</div>

{#if error}
  <p class="kits__error">API недоступен: {error}</p>
{/if}
