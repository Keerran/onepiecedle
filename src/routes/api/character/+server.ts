import { characters } from "$lib/server/characters";
import { json, type RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = ({ url }) => {
    const name = url.searchParams.get("name")
    const character = characters.find(char => char.name === name)
    return json(character)
}
