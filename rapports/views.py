import io

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from . import excel, pdf


def _annee(request):
    a = request.GET.get("annee")
    return int(a) if (a and a.isdigit()) else None


@login_required
def export_excel(request):
    annee = _annee(request)
    wb = excel.construire(annee)
    flux = io.BytesIO()
    wb.save(flux)
    flux.seek(0)
    nom = f"flotte_cab_{annee or 'global'}.xlsx"
    resp = HttpResponse(
        flux.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{nom}"'
    return resp


@login_required
def export_pdf(request):
    annee = _annee(request)
    contenu = pdf.construire(annee)
    nom = f"flotte_cab_{annee or 'global'}.pdf"
    resp = HttpResponse(contenu, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{nom}"'
    return resp
