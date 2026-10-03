from django import template

register = template.Library()


@register.filter
def call_attr(obj, attr_name):
    """
    Résout dynamiquement un attribut ou une méthode par son nom.

    Permet aux vues liste génériques de déclarer leurs colonnes sous forme
    de chaînes (ex. "get_type_engin_display", "vehicule", "montant_ttc").
    Retourne une chaîne vide pour les valeurs nulles.
    """
    try:
        value = getattr(obj, attr_name)
    except AttributeError:
        return ""
    if callable(value):
        try:
            value = value()
        except Exception:
            return ""
    if value is None:
        return ""
    if value is True:
        return "Oui"
    if value is False:
        return "Non"
    return value
