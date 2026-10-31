<script>
  import Glyph from './Glyph.svelte'

  let { devices = [], onmove } = $props()

  const position = (side) => (side === 'home' ? 0 : side === 'away' ? 1 : 0.5)
</script>

<section class="sides">
  <header class="sides__head">
    <h1 class="sides__title">Выбор стороны</h1>
  </header>

  <div class="sides__body">
    <div class="side side--home"><span class="side__label">Дома</span></div>
    <div class="side side--away"><span class="side__label">Гости</span></div>

    <div class="track">
      {#each devices as device (device.id)}
        <div class="track__row">
          <button
            class="device"
            class:is-off={!device.connected}
            style="--pos: {position(device.side)}; --tone: {device.tone}"
            onclick={(event) => {
              if (!device.connected) return
              const rect = event.currentTarget.getBoundingClientRect()
              onmove?.(device.id, event.clientX < rect.left + rect.width / 2 ? 'left' : 'right')
            }}
          >
            <Glyph name={device.type === 'gamepad' ? 'gamepad' : 'keyboard'} size={62} />
            {#if device.connected}
              {#if device.side !== 'home'}<span class="device__cue device__cue--left"></span>{/if}
              {#if device.side !== 'away'}<span class="device__cue device__cue--right"></span>{/if}
            {/if}
          </button>
        </div>
      {/each}
    </div>
  </div>
</section>
