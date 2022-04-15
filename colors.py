def load_colors(key: str = "candidat") -> dict:
    """
    Load the colors need in function of the key.

    Parameters
    ----------
    key : str
        The key to load the colors.

    Returns
    -------
    a dict of colors
    """
    if key == "candidat":
        return {
            "Marine Le Pen": {"couleur": "#04006e"},
            "Emmanuel Macron": {"couleur": "#0095eb"},
            "Yannick Jadot": {"couleur": "#0bb029"},
            "Jean-Luc Mélenchon": {"couleur": "#de001e"},
            "Arnaud Montebourg": {"couleur": "#940014"},
            "Fabien Roussel": {"couleur": "#940014"},
            "Valérie Pécresse": {"couleur": "#0242e3"},
            "Anne Hidalgo": {"couleur": "#b339a4"},
            "Christiane Taubira": {"couleur": "#c7a71a"},
            "Eric Zemmour": {"couleur": "#010038"},
            "Nathalie Arthaud": {"couleur": "#8f0007"},
            "Jean Lassalle": {"couleur": "#c96800"},
            "Philippe Poutou": {"couleur": "#82001a"},
            "François Asselineau": {"couleur": "#12004f"},
            "Nicolas Dupont-Aignan": {"couleur": "#3a84c4"},
        }
    if key == "methode":
        return {
            "jugement majoritaire": {"couleur": "#04006e"},
            "condorcet": {"couleur": "#0095eb"},
            "borda": {"couleur": "#0bb029"},
            "vote par assentiment simulé": {"couleur": "#de001e"},
            "vote par note": {"couleur": "#940014"},
        }
