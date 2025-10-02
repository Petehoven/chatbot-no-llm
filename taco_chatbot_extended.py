import json
import random
import re

# --- Woordenboek en grammatica modules ---
def load_json(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

woordenboek = load_json("woordenboek.json")
grammatica = load_json("grammatica.json")

def zoek_woord(woord):
    woord_lc = woord.lower()
    for entry in woordenboek:
        if entry["woord"].lower() == woord_lc:
            return entry
    return None

def analyse_zin(zin):
    woorden = re.findall(r"\w+", zin.lower())
    analyse = []
    for w in woorden:
        entry = zoek_woord(w)
        if entry:
            analyse.append({
                "woord": w,
                "soort": grammatica["woordsoorten"].get(entry["soort"], entry["soort"]),
                "betekenis": entry["betekenis"],
                "synoniemen": entry["synoniemen"]
            })
        else:
            analyse.append({"woord": w, "soort": "onbekend", "betekenis": "", "synoniemen": []})
    return analyse

def toon_analyse(analyse):
    return ', '.join([f"{a['woord']} ({a['soort']})" for a in analyse])

def analyseer_structuur(zin):
    woorden = re.findall(r"\w+", zin.lower())
    if len(woorden) >= 3 and woorden[0] == "ik" and woorden[1] == "ben":
        return {"onderwerp": woorden[0], "gezegde": woorden[1], "rest": ' '.join(woorden[2:])}
    elif len(woorden) >= 3 and woorden[0] == "wat" and woorden[1] == "ben" and woorden[2] == "jij":
        return {"vraag": "identiteit", "persoon": "Taco"}
    elif len(woorden) >= 3 and woorden[0] == "wat" and woorden[1] == "ben" and woorden[2] == "ik":
        return {"vraag": "identiteit", "persoon": "gebruiker"}
    return {}

# --- Verbeterde vraagherkenning ---
def detecteer_vraag(zin):
    zin_lc = zin.lower().strip()
    vraagwoorden = ["wat", "wie", "waar", "hoe", "wanneer", "waarom", "welke"]
    werkwoorden = ["ben", "heb", "is", "kan", "mag", "zal", "moet", "wil", "word", "doe", "gaan", "kunnen"]

    # 1. Eindigt op vraagteken
    if zin_lc.endswith("?"):
        return True

    # 2. Begint met vraagwoord
    for vw in vraagwoorden:
        if zin_lc.startswith(vw + " "):
            return True

    # 3. Begint met werkwoord gevolgd door onderwerp
    woorden = zin_lc.split()
    if len(woorden) >= 2 and woorden[0] in werkwoorden and woorden[1] in ["ik", "jij", "je", "hij", "zij", "het", "we", "wij", "jullie", "u", "taco"]:
        return True

    # 4. Bekende vraagpatronen met werkwoord + onderwerp
    if re.match(r".*\b(is|ben|heb|kan|mag|zal|moet|wil|word|doe|gaan|kunnen) (jij|je|ik|hij|zij|het|we|wij|jullie|u|taco)\b", zin_lc):
        return True

    return False

def categoriseer_vraag(zin, huidige_persoon):
    zin_lc = zin.lower()

    # Identiteit
    if ("wat ben jij" in zin_lc or "wie ben jij" in zin_lc):
        return "identiteit", "Taco"
    if ("wat ben ik" in zin_lc or "wie ben ik" in zin_lc):
        return "identiteit", "gebruiker"
    m_identiteit = re.search(r"wat ben (\w+)", zin_lc)
    if m_identiteit:
        naam = m_identiteit.group(1).capitalize()
        return "identiteit", naam

    # Eigenschap
    if ("wat is jouw eigenschap" in zin_lc or "wat zijn jouw eigenschappen" in zin_lc):
        return "eigenschap", "Taco"
    if ("wat is mijn eigenschap" in zin_lc or "wat zijn mijn eigenschappen" in zin_lc):
        return "eigenschap", "gebruiker"
    m_eigenschap = re.search(r"wat is (\w+) eigenschap", zin_lc)
    if m_eigenschap:
        naam = m_eigenschap.group(1).capitalize()
        return "eigenschap", naam

    # Locatie (waar)
    if ("waar woon jij" in zin_lc or "waar ben jij" in zin_lc):
        return "locatie", "Taco"
    if ("waar woon ik" in zin_lc or "waar ben ik" in zin_lc):
        return "locatie", "gebruiker"
    m_locatie = re.search(r"waar (woont|is|ben) (\w+)", zin_lc)
    if m_locatie:
        naam = m_locatie.group(2).capitalize()
        return "locatie", naam

    # Tijd (wanneer)
    if "wanneer" in zin_lc:
        if "ben jij" in zin_lc or "was jij" in zin_lc:
            return "tijd", "Taco"
        if "ben ik" in zin_lc or "was ik" in zin_lc:
            return "tijd", "gebruiker"
        m_tijd = re.search(r"wanneer (is|ben|was) (\w+)", zin_lc)
        if m_tijd:
            naam = m_tijd.group(2).capitalize()
            return "tijd", naam

    # Situatie (bijv. ziek, status)
    if "ziek" in zin_lc or "situatie" in zin_lc or "hoe gaat het" in zin_lc:
        if "jij" in zin_lc:
            return "situatie", "Taco"
        if "ik" in zin_lc:
            return "situatie", "gebruiker"
        m_situatie = re.search(r"situatie van (\w+)", zin_lc)
        if m_situatie:
            naam = m_situatie.group(1).capitalize()
            return "situatie", naam

    # Default: Onbekend
    return None, None

# --- Taco chatbot basis ---
personen = {}
taco_identiteiten = [
    "een pratende computer",
    "een chatbot",
    "een digitale gesprekspartner",
    "een virtuele assistent"
]

def opslaan_info(persoon, categorie, waarde):
    if persoon not in personen:
        personen[persoon] = {}
    if categorie not in personen[persoon]:
        personen[persoon][categorie] = []
    if waarde not in personen[persoon][categorie]:
        personen[persoon][categorie].append(waarde)

def zoek_info(persoon, categorie):
    if persoon == "gebruiker":
        persoon = actieve_persoon
    if persoon in personen and categorie in personen[persoon]:
        return personen[persoon][categorie][0]
    return None

def taco_antwoord(zin, huidige_persoon):
    if detecteer_vraag(zin):
        categorie, persoonnaam = categoriseer_vraag(zin, huidige_persoon)
        if categorie == "identiteit":
            if persoonnaam == "Taco":
                return f"Ik ben {random.choice(taco_identiteiten)}."
            else:
                eigenschap = zoek_info(persoonnaam, "eigenschap")
                if eigenschap:
                    return f"{persoonnaam} is {eigenschap}."
                else:
                    return f"Ik weet het nog niet over {persoonnaam}. Kan jij mij helpen?"
        elif categorie in ["eigenschap", "locatie", "tijd", "situatie"]:
            info = zoek_info(persoonnaam, categorie)
            if info:
                return f"{huidige_persoon.capitalize()} {categorie}: {info}"
            else:
                return f"Ik weet het nog niet over {huidige_persoon}. Kan jij mij helpen?"
        else:
            return "Ik weet het nog niet. Kan jij mij helpen?"
    return None

def suggestie_vraag(persoon):
    if persoon in personen:
        if "hobby" in personen[persoon]:
            return f"Wat doe je graag aan {personen[persoon]['hobby'][0]}?"
        if "locatie" in personen[persoon]:
            return f"Wat vind je leuk aan {personen[persoon]['locatie'][0]}?"
    return "Wil je nog meer vertellen?"

def toon_persoons_info(persoon):
    print(f"\n--- Overzicht van {persoon} ---")
    if persoon in personen:
        for categorie, waarden in personen[persoon].items():
            print(f"{categorie}: {', '.join(waarden)}")
    else:
        print("Geen gegevens gevonden.")
    print("----------------------------\n")

def main():
    global actieve_persoon
    print("Hallo! Ik ben Taco, jouw pratende computer.")
    actieve_persoon = input("Wie ben jij? ").capitalize()
    opslaan_info(actieve_persoon, "naam", actieve_persoon)
    opslaan_info("Taco", "naam", "Taco")
    for eig in taco_identiteiten:
        opslaan_info("Taco", "eigenschap", eig)
    print(f"Leuk je te ontmoeten, {actieve_persoon}!\nTyp 'STOP' om het gesprek te beëindigen.")

    while True:
        zin = input(f"{actieve_persoon}> ")
        zin_lc = zin.lower()
        if zin.strip().upper() == "STOP":
            break

        antwoord = taco_antwoord(zin, actieve_persoon)
        if antwoord:
            print(f"Taco> {antwoord}")
        else:
            analyse = analyse_zin(zin)
            print(f"Taco> Woordanalyse: {toon_analyse(analyse)}")
            structuur = analyseer_structuur(zin)
            # Eigenschap opslaan "Ik ben ..."
            if structuur.get("onderwerp") == "ik" and structuur.get("gezegde") == "ben":
                eigenschap = structuur.get("rest", "")
                opslaan_info(actieve_persoon, "eigenschap", eigenschap)
                print(f"Taco> Ik onthoud dat jij {eigenschap} bent.")
            # Locatie (ik woon in ... OF ik ben in ...)
            elif zin_lc.startswith("ik woon in "):
                locatie = zin[11:].strip()
                opslaan_info(actieve_persoon, "locatie", locatie)
                print(f"Taco> Ik onthoud dat jij woont in {locatie}.")
            elif zin_lc.startswith("ik ben in "):
                locatie = zin[10:].strip()
                opslaan_info(actieve_persoon, "locatie", locatie)
                print(f"Taco> Ik onthoud dat jij bent in {locatie}.")
            # Tijd (ik ben geboren in ...)
            elif zin_lc.startswith("ik ben geboren in "):
                tijd = zin[18:].strip()
                opslaan_info(actieve_persoon, "tijd", tijd)
                print(f"Taco> Ik onthoud dat jij geboren bent in {tijd}.")
            # Situatie (ik ben ziek)
            elif "ik ben ziek" in zin_lc:
                opslaan_info(actieve_persoon, "situatie", "ziek")
                print("Taco> Beterschap! Ik onthoud dat jij ziek bent.")
            else:
                print(f"Taco> Interessant! Wil je nog iets vertellen?")
            print(f"Taco> {suggestie_vraag(actieve_persoon)}")

    toon_persoons_info(actieve_persoon)
    toon_persoons_info("Taco")
    print("Tot ziens!")

if __name__ == "__main__":
    main()