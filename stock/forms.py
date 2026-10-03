from core.forms import BootstrapModelForm, DateInputFr

from .models import Article, MouvementStock


class ArticleForm(BootstrapModelForm):
    class Meta:
        model = Article
        fields = [
            "code", "designation", "specification", "categorie",
            "stock_initial", "seuil_mini", "observation",
        ]


class MouvementStockForm(BootstrapModelForm):
    class Meta:
        model = MouvementStock
        fields = ["date", "article", "type", "quantite", "motif", "responsable"]
        widgets = {"date": DateInputFr()}
