import type { Character } from "$lib/server/characters";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
    const answer: Character = await fetch("api/character/random").then((res) => res.json());
    return { answer }
}
