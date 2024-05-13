import fs from "fs/promises";
import { parse, type CastingContext } from "csv-parse/sync";

export interface Character {
    name: string,

}

function cast(value: string, context: CastingContext) {
    switch (context.column) {
        case "anime_debut":
        case "manga_debut":
        case "bounty":
        case "height":
            return parseInt(value);
        case "aliases":
            return value.split(",");
        case "haoshoku":
        case "kenbunshoku":
        case "busoshoku":
            switch(value) {
                case "True":
                    return true;
                case "False":
                    return false;
                default:
                    throw new Error(`Invalid value for ${context}: ${value}`);
            }
        default:
            return value;
    }
}

const file = await fs.readFile("./choices.csv", "utf8");

export const characters: Character[] = parse(file, { columns: true, cast });
