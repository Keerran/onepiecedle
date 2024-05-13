<script lang="ts">
    import type { Character } from "$lib/server/characters";

    let search = "";
    let character: Character | null = null;

    async function getCharacter() {
        character = await fetch(`/api/character?name=${search}`).then(r => r.json());
    }
</script>

<form on:submit|preventDefault={getCharacter}>
    <input type="text" name="name" bind:value={search} />
    <input type="submit" />
</form>

{JSON.stringify(character)}
