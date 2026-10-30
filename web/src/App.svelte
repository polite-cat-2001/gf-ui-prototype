<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import Controls from './lib/Controls.svelte'
  import TabBar from './lib/TabBar.svelte'
  import TileGrid from './lib/TileGrid.svelte'
  import MenuPanel from './lib/MenuPanel.svelte'

  const tabs = [
    { id: 'play', label: 'Играть' },
    { id: 'settings', label: 'Настройки' },
  ]

  const playTiles = [
    {
      id: 'resume',
      title: 'Продолжить карьеру',
      sub: 'Возвращение к последнему сохранению',
      match: { label: 'Следующий матч', value: 'Барселона — Реал' },
      glyph: 'trophy',
      col: 1,
      row: 1,
      colSpan: 2,
      rowSpan: 2,
    },
    {
      id: 'quick',
      title: 'Быстрый матч',
      sub: 'Один, вдвоём или ИИ против ИИ',
      tags: ['1 игрок', '2 игрока', 'ИИ'],
      glyph: 'play',
      col: 3,
      row: 1,
      colSpan: 2,
      rowSpan: 1,
    },
    {
      id: 'career',
      title: 'Карьера',
      sub: 'Продолжить, новая, загрузить',
      glyph: 'shirt',
      col: 3,
      row: 2,
      colSpan: 1,
      rowSpan: 1,
    },
    {
      id: 'network',
      title: 'Сетевой матч',
      sub: 'Хост или клиент',
      glyph: 'network',
      col: 4,
      row: 2,
      colSpan: 1,
      rowSpan: 1,
    },
  ]

  const settingsTiles = [
    { id: 'gameplay', title: 'Геймплей', sub: 'Сложность и помощники', glyph: 'sliders', col: 1, row: 1, colSpan: 2, rowSpan: 1 },
    { id: 'controls', title: 'Управление', sub: 'Клавиатура и геймпады', glyph: 'gamepad', col: 3, row: 1, colSpan: 2, rowSpan: 1 },
    { id: 'graphics', title: 'Графика', sub: 'Экран и качество', glyph: 'monitor', col: 1, row: 2, colSpan: 2, rowSpan: 1 },
    { id: 'audio', title: 'Звук', sub: 'Музыка и эффекты', glyph: 'volume', col: 3, row: 2, colSpan: 2, rowSpan: 1 },
  ]

  const panels = {
    resume: {
      title: 'Продолжить карьеру',
      note: 'Демо-сохранение: «Барселона», третий тур Примеры. Настоящих сейвов в прототипе пока нет.',
      rows: [
        { title: 'Загрузить сохранение', sub: 'Барселона · 3-й тур' },
        { title: 'Начать новую карьеру', sub: 'Выбор клуба и лиги' },
      ],
    },
    quick: {
      title: 'Быстрый матч',
      note: 'Локальный матч на одном экране или матч против ИИ.',
      rows: [
        { title: 'Один игрок', sub: 'Клавиатура или геймпад' },
        { title: 'Два игрока', sub: 'Два геймпада' },
        { title: 'ИИ против ИИ', sub: 'Демонстрационный матч' },
      ],
    },
    career: {
      title: 'Карьера',
      note: 'Тренерская карьера: клуб, сезон, трансферы.',
      rows: [
        { title: 'Продолжить', sub: 'Барселона · 3-й тур' },
        { title: 'Новая карьера', sub: 'Выбор клуба' },
        { title: 'Загрузить', sub: 'Список сохранений' },
      ],
    },
    network: {
      title: 'Сетевой матч',
      note: 'Прямое подключение между двумя игроками.',
      rows: [
        { title: 'Хост', sub: 'Создать матч' },
        { title: 'Клиент', sub: 'Подключиться по адресу' },
      ],
    },
    gameplay: { title: 'Геймплей', note: 'Сложность, помощники и длительность матча. Раздел в работе.', rows: [] },
    controls: { title: 'Управление', note: 'Раскладка клавиатуры и функции геймпада. Раздел в работе.', rows: [] },
    graphics: { title: 'Графика', note: 'Разрешение, качество и эффекты. Раздел в работе.', rows: [] },
    audio: { title: 'Звук', note: 'Музыка, комментатор и эффекты. Раздел в работе.', rows: [] },
  }

  let meta = $state(null)
  let error = $state('')
  let tabIndex = $state(0)
  let zone = $state('grid')
  let tileIndex = $state(0)
  let rowIndex = $state(0)
  let stack = $state([])
  let enterDir = $state(0)
  let enterTimer

  const tiles = $derived(tabIndex === 0 ? playTiles : settingsTiles)
  const top = $derived(stack.length ? stack[stack.length - 1] : null)

  const hints = $derived.by(() => {
    if (top) {
      return top.rows?.length
        ? [
            { keys: ['↑', '↓'], label: 'Выбор' },
            { keys: ['Enter'], label: 'Открыть' },
            { keys: ['Esc'], label: 'Назад' },
          ]
        : [{ keys: ['Esc'], label: 'Назад' }]
    }
    if (zone === 'tabs') {
      return [
        { keys: ['←', '→'], label: 'Разделы' },
        { keys: ['↓'], label: 'К тайлам' },
      ]
    }
    return [
      { keys: ['↑', '↓', '←', '→'], label: 'Движение' },
      { keys: ['Enter'], label: 'Выбрать' },
    ]
  })

  onMount(async () => {
    try {
      meta = await api.meta()
    } catch (caught) {
      error = caught.message
    }
  })

  function selectTab(index, source = 'key') {
    const direction = index === tabIndex ? 0 : index > tabIndex ? 1 : -1
    tabIndex = index
    tileIndex = 0
    rowIndex = 0
    stack = []
    zone = source === 'click' ? 'grid' : 'tabs'

    if (direction !== 0) {
      enterDir = direction
      clearTimeout(enterTimer)
      enterTimer = setTimeout(() => (enterDir = 0), 560)
    }
  }

  function push(panel) {
    stack.push(panel)
    rowIndex = 0
  }

  function back() {
    stack.pop()
    rowIndex = 0
  }

  function openTile(tile) {
    const panel = panels[tile.id]
    if (panel) push(panel)
  }

  function pickRow(row) {
    push({
      title: row.title,
      note: 'Экран в работе: дальше здесь будут выбор команды, параметры матча и состав.',
      rows: [],
    })
  }

  function neighbor(index, direction) {
    const from = tiles[index]
    const fromColEnd = from.col + from.colSpan - 1
    const fromRowEnd = from.row + from.rowSpan - 1

    let best = null
    let bestScore = Infinity

    tiles.forEach((tile, i) => {
      if (i === index) return

      const colEnd = tile.col + tile.colSpan - 1
      const rowEnd = tile.row + tile.rowSpan - 1
      let primary = 0
      let gap = 0

      if (direction === 'right') {
        if (tile.col <= fromColEnd) return
        primary = tile.col - fromColEnd
        gap = Math.max(0, from.row - rowEnd, tile.row - fromRowEnd)
      } else if (direction === 'left') {
        if (colEnd >= from.col) return
        primary = from.col - colEnd
        gap = Math.max(0, from.row - rowEnd, tile.row - fromRowEnd)
      } else if (direction === 'down') {
        if (tile.row <= fromRowEnd) return
        primary = tile.row - fromRowEnd
        gap = Math.max(0, from.col - colEnd, tile.col - fromColEnd)
      } else {
        if (rowEnd >= from.row) return
        primary = from.row - rowEnd
        gap = Math.max(0, from.col - colEnd, tile.col - fromColEnd)
      }

      const score = primary + gap * 100
      if (score < bestScore) {
        bestScore = score
        best = i
      }
    })

    return best
  }

  function edgeIndex(list, row, side) {
    let best = 0
    let bestValue = side === 'left' ? Infinity : -Infinity

    list.forEach((tile, i) => {
      const coversRow = tile.row <= row && row < tile.row + tile.rowSpan
      if (!coversRow) return
      const value = side === 'left' ? tile.col : tile.col + tile.colSpan
      if (side === 'left' ? value < bestValue : value > bestValue) {
        bestValue = value
        best = i
      }
    })

    return best
  }

  function switchByEdge(direction) {
    const row = tiles[tileIndex].row
    const step = direction === 'right' ? 1 : tabs.length - 1
    const nextTab = (tabIndex + step) % tabs.length
    const list = nextTab === 0 ? playTiles : settingsTiles

    tabIndex = nextTab
    stack = []
    rowIndex = 0
    zone = 'grid'
    tileIndex = edgeIndex(list, row, direction === 'right' ? 'left' : 'right')

    enterDir = direction === 'right' ? 1 : -1
    clearTimeout(enterTimer)
    enterTimer = setTimeout(() => (enterDir = 0), 560)
  }

  function handleKeydown(event) {
    if (top) {
      if (event.key === 'Escape') {
        event.preventDefault()
        back()
        return
      }
      if (!top.rows?.length) return
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        rowIndex = Math.min(top.rows.length - 1, rowIndex + 1)
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        rowIndex = Math.max(0, rowIndex - 1)
      } else if (event.key === 'Enter') {
        event.preventDefault()
        pickRow(top.rows[rowIndex])
      }
      return
    }

    if (zone === 'tabs') {
      if (event.key === 'ArrowRight') {
        event.preventDefault()
        selectTab((tabIndex + 1) % tabs.length)
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault()
        selectTab((tabIndex + tabs.length - 1) % tabs.length)
      } else if (event.key === 'ArrowDown' || event.key === 'Enter') {
        event.preventDefault()
        zone = 'grid'
      }
      return
    }

    if (event.key === 'ArrowUp' && tiles[tileIndex].row === 1) {
      event.preventDefault()
      zone = 'tabs'
      return
    }

    const directions = {
      ArrowRight: 'right',
      ArrowLeft: 'left',
      ArrowUp: 'up',
      ArrowDown: 'down',
    }

    if (directions[event.key]) {
      event.preventDefault()
      const direction = directions[event.key]
      const next = neighbor(tileIndex, direction)
      if (next != null) {
        tileIndex = next
        return
      }
      if (direction === 'right' || direction === 'left') switchByEdge(direction)
      return
    }

    if (event.key === 'Enter') {
      event.preventDefault()
      openTile(tiles[tileIndex])
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="stage">
  <img class="stage__photo" src="/stadium.jpg" alt="" />
</div>

<div class="app">
  <div class="status" class:is-error={error}>
    {#if error}
      API недоступен: {error}
    {:else if meta}
      канон: {meta.counts.clubs} клубов · {meta.counts.players} игроков
    {:else}
      подключение к API…
    {/if}
  </div>

  <div class="frame">
    <div class="panel-wrap">
      <TabBar {tabs} index={tabIndex} focused={zone === 'tabs'} onselect={selectTab} />

      {#if top}
        <MenuPanel
          title={top.title}
          note={top.note}
          rows={top.rows ?? []}
          selected={rowIndex}
          onhover={(i) => (rowIndex = i)}
          onpick={(i) => pickRow(top.rows[i])}
        />
      {:else}
        <TileGrid
          {tiles}
          selected={tileIndex}
          active={zone === 'grid'}
          enter={enterDir}
          onhover={(i) => {
            tileIndex = i
            zone = 'grid'
          }}
          onpick={(i) => {
            tileIndex = i
            openTile(tiles[i])
          }}
        />
      {/if}

      <div class="legend">
        <Controls {hints} />
      </div>
    </div>
  </div>

  <div class="brand">GF <span>UI</span></div>
</div>
