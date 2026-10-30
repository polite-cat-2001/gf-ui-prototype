<script>
  let { hints = [] } = $props()
</script>

<div class="control-hints">
  {#each hints as hint}
    <span class="control-hint">
      {#each hint.keys as key}<kbd>{key}</kbd>{/each}
      <span>{hint.label}</span>
    </span>
  {/each}
</div>
