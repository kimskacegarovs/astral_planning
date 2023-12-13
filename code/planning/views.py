from django.shortcuts import render, reverse, redirect, HttpResponse
from django.views.generic import TemplateView, View, FormView
from .service import PlanningService, PlanningRequest, PlanningFactory
from .forms import LocationSearchForm
import json
import requests
from dataclasses import dataclass


class PlanningView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apply_planning_url"] = reverse("apply_planning")
        context["location_search_form"] = LocationSearchForm()
        return context


class ResourcesView(TemplateView):
    template_name = "resources.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["planning_set"] = PlanningService().get_planning_set()
        return context


class ApplyPlanningView(View):
    def post(self, request, *args, **kwargs):
        planning_request = PlanningRequest(**json.loads(self.request.POST["planning_request"]))
        PlanningService().apply_planning(planning_request=planning_request)
        return redirect("resources")


class CancelPlanningView(View):
    def post(self, request, *args, **kwargs):
        planning_request = PlanningRequest(
            transport_id=self.request.POST["transport_id"],
            shipment_id=self.request.POST["shipment_id"],
        )
        PlanningService().cancel_planning(planning_request=planning_request)
        return redirect("resources")


@dataclass
class LocationSearchResult:
    display_name: str
    coordinates: str


class GeocodingView(FormView):
    form_class = LocationSearchForm

    def form_valid(self, form):
        search = form.cleaned_data["search"]
        search_results = self.search(search)
        return render(self.request, "location_search_results.html", {"search_results": search_results})

    def search(self, search: str) -> list[LocationSearchResult]:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {"format": "json", "q": search}
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        results = [
            LocationSearchResult(
                display_name=result["display_name"],
                coordinates=f"{result['lat']}, {result['lon']}"
            )
            for result in response.json()
        ]
        return results


