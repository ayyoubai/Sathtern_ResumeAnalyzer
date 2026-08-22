import re


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_extracted_text(text: str) -> str:
    """
    Cleans text extracted from a PDF.

    Fixes:
    - Separated characters: A y y o u b -> Ayyoub
    - Artificial spaces around @ and .
    - Separated phone numbers
    - Glued words from PDF extraction
    - Multiple spaces

    IMPORTANT:
    We avoid globally removing spaces between letters,
    as this could break normal sentences.
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
            # Isolated letter sequences
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

                # Rebuild only if sequence has at least 2 characters
                if len(sequence) >= 2:

                    cleaned_words.append(
                        "".join(sequence)
                    )

                    i = j
                    continue

            # =================================================
            # Isolated digit sequences
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
        # PUNCTUATION CLEANUP
        # =====================================================

        line = re.sub(
            r"\s+([,.;:!?])",
            r"\1",
            line
        )

        line = re.sub(
            r"([(\[{])\s+",
            r"\1",
            line
        )

        line = re.sub(
            r"\s+([)\]}])",
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
    # EMAIL NORMALIZATION
    # ============================================================

    # ayyoub . ai20 @ gmail . com -> ayyoub.ai20@gmail.com

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
    # PHONE NORMALIZATION
    # ============================================================

    # + 2 1 2 6 5 3 6 0 8 3 7 2 -> +212653608372

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
    # COMMON PDF GLUED WORD FIXES
    # ============================================================

    # These are common patterns found in PDF extraction.
    # Add more patterns as needed for your use case.

    replacements = {

        # Identity
        "AyyoubELMAHI": "Ayyoub ELMAHI",

        # Profile
        "\u00c9tudianting\u00e9nieuren": "\u00c9tudiant ing\u00e9nieur en",
        "sp\u00e9cialis\u00e9eng\u00e9nieinformatique": "sp\u00e9cialis\u00e9 en g\u00e9nie informatique",

        # Sections
        "Exp\u00e9riencesprofessionnelles": "Exp\u00e9riences professionnelles",
        "Comp\u00e9tencestechniques": "Comp\u00e9tences techniques",
        "Comp\u00e9tencescomportementales": "Comp\u00e9tences comportementales",
        "Dipl\u00f4mesetFormations": "Dipl\u00f4mes et Formations",
        "Exp\u00e9riencesacad\u00e9miques": "Exp\u00e9riences acad\u00e9miques",

        # Education
        "Cycled'ing\u00e9nierie": "Cycle d'ing\u00e9nierie",
        "Cycle d ' ing\u00e9nierie": "Cycle d'ing\u00e9nierie",
        "Cycled ' ing\u00e9nierie": "Cycle d'ing\u00e9nierie",
        "G\u00e9nieInformatique": "G\u00e9nie Informatique",
        "\u00c9coledesHautes\u00c9tudes": "\u00c9cole des Hautes \u00c9tudes",
        "DTSen": "DTS en",
        "D\u00e9veloppementDigital": "D\u00e9veloppement Digital",
        "OptionFullStack": "Option Full Stack",

        # Skills
        "Gestiondebasesdedonn\u00e9es": "Gestion de bases de donn\u00e9es",
        "OutilsDevops": "Outils DevOps",
        "Outilsded\u00e9veloppement": "Outils de d\u00e9veloppement",
        "Languages & Framworks": "Languages & Frameworks",

        # Experiences
        "Staged\u00e9veloppeurFullStack": "Stage d\u00e9veloppeur Full Stack",
        "STEFASTBENCAR": "STE FASTBENCAR",

        # Projects
        "ProjetdeSynth\u00e8sed\u00e9veloppeurFullStack": "Projet de Synth\u00e8se d\u00e9veloppeur Full Stack",
        "Projetdefind'ann\u00e9e": "Projet de fin d'ann\u00e9e",
        "Projetdefind ' ann\u00e9e": "Projet de fin d'ann\u00e9e",
        "D\u00e9veloppementfull-stack": "D\u00e9veloppement full-stack",
        "D\u00e9veloppementfull - stack": "D\u00e9veloppement full-stack",

        # Database
        "Basededonn\u00e9es": "Base de donn\u00e9es",
        "Basededonn\u00e9esMySQL": "Base de donn\u00e9es MySQL",
        "Basededonn\u00e9esSqlServer": "Base de donn\u00e9es SQL Server",
        "Basededonn\u00e9esSQLServer": "Base de donn\u00e9es SQL Server",

        # Users / Auth
        "authentificationet": "authentification et",
        "Gestiondesutilisateurs": "Gestion des utilisateurs",
    }

    for old, new in replacements.items():
        result = result.replace(old, new)

    # ============================================================
    # FINAL CLEANUP
    # ============================================================

    result = re.sub(
        r"[ \t]+",
        " ",
        result
    )

    return result.strip()


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_email(text: str) -> str | None:
    """
    Extracts an email address from the text.

    Supports:
        ayyoub.ai20@gmail.com
        ayyoub.ai20 @ gmail.com
        ayyoub.ai20 @ gmail . com
    """

    if not text:
        return None

    # Process line by line to avoid creating fake emails
    # from unrelated text across multiple lines

    for line in text.splitlines():

        if "@" not in line:
            continue

        candidate = line.strip()

        # Remove spaces around @
        candidate = re.sub(
            r"\s*@\s*",
            "@",
            candidate
        )

        # Remove spaces around dots only in email-like zones
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

            # Simple validation
            if (
                "@" in email
                and "." in email.split("@")[-1]
                and len(email) >= 6
            ):
                return email

    return None


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phone(text: str) -> str | None:
    """
    Extracts a Moroccan phone number.

    Supports:
        +212653608372
        +212 653 608 372
        + 2 1 2 6 5 3 6 0 8 3 7 2
    """

    if not text:
        return None

    # Case 1: Standard +212 format
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

    # Case 2: Spaced digits
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
# NAME EXTRACTION
# ============================================================

def extract_name(text: str) -> str | None:
    """
    Extracts the candidate name.

    The name is usually located in the first few lines.
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
        "Exp\u00e9riences professionnelles",
        "Comp\u00e9tences techniques",
        "Comp\u00e9tences comportementales",
        "Dipl\u00f4mes et Formations",
        "Exp\u00e9riences acad\u00e9miques",
        "Profil",
        "Comp\u00e9tences",
        "Formation",
        "Exp\u00e9riences",
        "Projets",
        # English variants
        "Languages",
        "Professional Experiences",
        "Technical Skills",
        "Soft Skills",
        "Education",
        "Academic Experiences",
        "Profile",
        "Skills",
        "Experience",
        "Projects",
        "Certifications",
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

        # A name line usually contains at least one uppercase letter
        if not any(
            char.isupper()
            for char in line
            if char.isalpha()
        ):
            continue

        return line

    return None


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location(text: str) -> str | None:
    """
    Extracts a known city from the resume text.
    """

    if not text:
        return None

    locations = [
        "Oujda",
        "Casablanca",
        "Rabat",
        "F\u00e8s",
        "Fes",
        "Marrakech",
        "Tanger",
        "Tangier",
        "Agadir",
        "Mekn\u00e8s",
        "Meknes",
    ]

    text_lower = text.lower()

    for location in locations:

        if location.lower() in text_lower:

            # Normalize variants
            if location.lower() == "fes":
                return "F\u00e8s"

            if location.lower() == "meknes":
                return "Mekn\u00e8s"

            if location.lower() == "tangier":
                return "Tanger"

            return location

    return None
