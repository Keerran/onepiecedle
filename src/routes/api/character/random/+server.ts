import { characters } from "$lib/server/characters";
import { json, type RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = () => {
    const character = characters[Math.floor(Math.random() * characters.length)]
    return json(character)
}
