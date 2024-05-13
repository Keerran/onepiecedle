<script lang="ts">
    import type { PageData } from "./$types";

    export let data: PageData;

    let { answer } = data;
    let search = "";

    async function getCharacter() {
    }
</script>

<form on:submit|preventDefault={getCharacter}>
    <input type="text" name="name" bind:value={search} />
    <input type="submit" />
</form>

{JSON.stringify(answer)}
