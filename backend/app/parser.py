import re


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_extracted_text(text: str) -> str:
    """
    Nettoie le texte extrait d'un PDF.

    Corrige notamment :
    - caractères séparés : A y y o u b -> Ayyoub
    - espaces artificiels autour de @ et .
    - numéros de téléphone séparés
    - mots collés provenant du PDF
    - espaces multiples

    IMPORTANT :
    On évite de supprimer globalement les espaces entre lettres,
    car cela pourrait transformer des phrases normales.
    """

    if not text:
        return ""

    lines = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        words = line.split()

        cleaned_words = []
        i = 0

        while i < len(words):

            word = words[i]

            # =================================================
            # Séquence de lettres isolées
            # =================================================

            if len(word) == 1 and word.isalpha():

                sequence = [word]
                j = i + 1

                while j < len(words):

                    next_word = words[j]

                    if len(next_word) == 1 and next_word.isalpha():
                        sequence.append(next_word)
                        j += 1
                    else:
                        break

                # Reconstruire seulement si la séquence
                # contient au moins 2 caractères.
                if len(sequence) >= 2:

                    cleaned_words.append(
                        "".join(sequence)
                    )

                    i = j
                    continue

            # =================================================
            # Séquence de chiffres isolés
            # =================================================

            if len(word) == 1 and word.isdigit():

                sequence = [word]
                j = i + 1

                while j < len(words):

                    next_word = words[j]

                    if len(next_word) == 1 and next_word.isdigit():
                        sequence.append(next_word)
                        j += 1
                    else:
                        break

                if len(sequence) >= 2:

                    cleaned_words.append(
                        "".join(sequence)
                    )

                    i = j
                    continue

            cleaned_words.append(word)

            i += 1

        line = " ".join(cleaned_words)

        # =====================================================
        # PONCTUATION
        # =====================================================

        line = re.sub(
            r"\s+([,.;:!?])",
            r"\1",
            line
        )

        line = re.sub(
            r"([(\[])\s+",
            r"\1",
            line
        )

        line = re.sub(
            r"\s+([)\]])",
            r"\1",
            line
        )

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        lines.append(line.strip())

    result = "\n".join(lines)

    # ============================================================
    # EMAIL - NORMALISATION
    # ============================================================

    # ayyoub . ai20 @ gmail . com
    # ->
    # ayyoub.ai20@gmail.com

    result = re.sub(
        r"([A-Za-z0-9._%+\-]+)\s*@\s*",
        r"\1@",
        result
    )

    result = re.sub(
        r"([A-Za-z0-9._%+\-]+)\s*\.\s*"
        r"(?=[A-Za-z]{2,})",
        r"\1.",
        result
    )

    result = re.sub(
        r"(?<=[A-Za-z0-9])\s*@\s*",
        "@",
        result
    )

    # ============================================================
    # TELEPHONE
    # ============================================================

    # + 2 1 2 6 5 3 6 0 8 3 7 2
    # ->
    # +212653608372

    result = re.sub(
        r"\+\s*2\s*1\s*2"
        r"(?:\s*\d){9}",
        lambda match: "+" + re.sub(
            r"\s+",
            "",
            match.group(0)[1:]
        ),
        result
    )

    # ============================================================
    # CORRECTIONS DE MOTS COLLÉS
    # ============================================================

    replacements = {

        # ======================================================
        # IDENTITÉ
        # ======================================================

        "AyyoubELMAHI":
            "Ayyoub ELMAHI",

        # ======================================================
        # PROFIL
        # ======================================================

        "Étudiantingénieuren":
            "Étudiant ingénieur en",

        "spécialiséengénieinformatique":
            "spécialisé en génie informatique",

        # ======================================================
        # SECTIONS
        # ======================================================

        "Expériencesprofessionnelles":
            "Expériences professionnelles",

        "Compétencestechniques":
            "Compétences techniques",

        "Compétencescomportementales":
            "Compétences comportementales",

        "DiplômesetFormations":
            "Diplômes et Formations",

        "Expériencesacadémiques":
            "Expériences académiques",

        # ======================================================
        # EDUCATION
        # ======================================================

        "Cycled'ingénierie":
            "Cycle d'ingénierie",

        "Cycle d ' ingénierie":
            "Cycle d'ingénierie",

        "Cycled ' ingénierie":
            "Cycle d'ingénierie",

        "GénieInformatique":
            "Génie Informatique",

        "ÉcoledesHautesÉtudes":
            "École des Hautes Études",

        "DTSen":
            "DTS en",

        "DéveloppementDigital":
            "Développement Digital",

        "OptionFullStack":
            "Option Full Stack",

        # ======================================================
        # SKILLS
        # ======================================================

        "Gestiondebasesdedonnées":
            "Gestion de bases de données",

        "OutilsDevops":
            "Outils DevOps",

        "Outilsdedéveloppement":
            "Outils de développement",

        "Languages & Framworks":
            "Languages & Frameworks",

        # ======================================================
        # EXPERIENCES
        # ======================================================

        "StagedéveloppeurFullStack":
            "Stage développeur Full Stack",

        "STEFASTBENCAR":
            "STE FASTBENCAR",

        # ======================================================
        # PROJECTS
        # ======================================================

        "ProjetdeSynthèsedéveloppeurFullStack":
            "Projet de Synthèse développeur Full Stack",

        "Projetdefind'année":
            "Projet de fin d'année",

        "Projetdefind ' année":
            "Projet de fin d'année",

        "Développementfull-stack":
            "Développement full-stack",

        "Développementfull - stack":
            "Développement full-stack",

        # ======================================================
        # DATABASE
        # ======================================================

        "Basededonnées":
            "Base de données",

        "BasededonnéesMySQL":
            "Base de données MySQL",

        "BasededonnéesSqlServer":
            "Base de données SQL Server",

        "BasededonnéesSQLServer":
            "Base de données SQL Server",

        # ======================================================
        # USERS / AUTH
        # ======================================================

        "authentificationet":
            "authentification et",

        "Gestiondesutilisateurs":
            "Gestion des utilisateurs",
    }

    for old, new in replacements.items():
        result = result.replace(old, new)

    # ============================================================
    # NETTOYAGE FINAL
    # ============================================================

    result = re.sub(
        r"[ \t]+",
        " ",
        result
    )

    return result.strip()


# ============================================================
# EMAIL
# ============================================================

def extract_email(text: str):
    """
    Extrait une adresse email.

    Supporte notamment :

        ayyoub.ai20@gmail.com

        ayyoub.ai20 @ gmail.com

        ayyoub.ai20 @ gmail . com
    """

    if not text:
        return None

    # --------------------------------------------------------
    # On travaille ligne par ligne afin d'éviter de créer
    # accidentellement un email à partir de plusieurs lignes.
    # --------------------------------------------------------

    for line in text.splitlines():

        if "@" not in line:
            continue

        candidate = line.strip()

        # ----------------------------------------------------
        # Supprimer les espaces autour de @
        # ----------------------------------------------------

        candidate = re.sub(
            r"\s*@\s*",
            "@",
            candidate
        )

        # ----------------------------------------------------
        # Supprimer les espaces autour des points
        # uniquement dans les zones ressemblant à un email.
        # ----------------------------------------------------

        candidate = re.sub(
            r"([A-Za-z0-9._%+\-]+)"
            r"\s*\.\s*"
            r"([A-Za-z]{2,})",
            r"\1.\2",
            candidate
        )

        candidate = re.sub(
            r"([A-Za-z0-9.-]+)"
            r"\s*\.\s*"
            r"([A-Za-z]{2,})",
            r"\1.\2",
            candidate
        )

        match = re.search(
            r"[A-Za-z0-9._%+\-]+"
            r"@"
            r"[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}",
            candidate
        )

        if match:

            email = match.group(0).strip()

            # ------------------------------------------------
            # Validation simple
            # ------------------------------------------------

            if (
                "@" in email
                and "." in email.split("@")[-1]
                and len(email) >= 6
            ):
                return email

    return None


# ============================================================
# PHONE
# ============================================================

def extract_phone(text: str):
    """
    Extrait un numéro marocain.

    Supporte :

        +212653608372

        +212 653 608 372

        + 2 1 2 6 5 3 6 0 8 3 7 2
    """

    if not text:
        return None

    # ========================================================
    # CAS 1 : +212 classique
    # ========================================================

    match = re.search(
        r"\+212[\s.-]?"
        r"\d[\d\s.-]{7,12}\d",
        text
    )

    if match:

        digits = re.sub(
            r"\D",
            "",
            match.group(0)
        )

        if (
            digits.startswith("212")
            and len(digits) == 12
        ):
            return "+" + digits

    # ========================================================
    # CAS 2 : chiffres séparés
    # ========================================================

    for line in text.splitlines():

        if "+" not in line:
            continue

        digits = re.sub(
            r"\D",
            "",
            line
        )

        if (
            digits.startswith("212")
            and len(digits) == 12
        ):
            return "+" + digits

    return None


# ============================================================
# NAME
# ============================================================

def extract_name(text: str):
    """
    Extrait le nom du candidat.

    Le nom est généralement situé dans les premières lignes.
    """

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    ignored = {
        "Langues",
        "Expériences professionnelles",
        "Compétences techniques",
        "Compétences comportementales",
        "Diplômes et Formations",
        "Expériences académiques",
        "Profil",
        "Compétences",
        "Formation",
        "Expériences",
        "Projets",
    }

    for line in lines[:10]:

        if line in ignored:
            continue

        if "@" in line:
            continue

        if "+" in line:
            continue

        if re.search(r"\d", line):
            continue

        words = line.split()

        if not (1 <= len(words) <= 4):
            continue

        # Une ligne de nom contient généralement
        # au moins une lettre majuscule.
        if not any(
            char.isupper()
            for char in line
            if char.isalpha()
        ):
            continue

        return line

    return None


# ============================================================
# LOCATION
# ============================================================

def extract_location(text: str):
    """
    Extrait une ville connue du CV.
    """

    if not text:
        return None

    locations = [
        "Oujda",
        "Casablanca",
        "Rabat",
        "Fès",
        "Fes",
        "Marrakech",
        "Tanger",
        "Tangier",
        "Agadir",
        "Meknès",
        "Meknes",
    ]

    text_lower = text.lower()

    for location in locations:

        if location.lower() in text_lower:

            # Uniformiser Fes -> Fès
            if location.lower() == "fes":
                return "Fès"

            if location.lower() == "meknes":
                return "Meknès"

            if location.lower() == "tangier":
                return "Tanger"

            return location

    return None