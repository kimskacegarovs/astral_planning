from django.shortcuts import render, reverse, redirect, HttpResponse
from django.views.generic import TemplateView, View, FormView
from .service import PlanningService, PlanningRequest, PlanningFactory
from .forms import LocationSearchForm, LocationForm
from .geo_service import GeoService
from .types import LocationSearchResult
import json


class PlanningView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apply_planning_url"] = reverse("apply_planning")
        context["location_form"] = LocationForm()
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


class LocationSearchView(FormView):
    form_class = LocationSearchForm

    def form_valid(self, form):
        search_results = GeoService().search(search=form.cleaned_data["search"])
        return render(self.request, "location_search_results.html", {"search_results": search_results})


class LocationSearchResultSelectView(View):
    def post(self, request, *args, **kwargs):
        result = LocationSearchResult.from_json(self.request.POST["result"])
        form = LocationForm(initial={"location": result.display_name, "coordinates": result.coordinates})
        context = {"location_form": form, "location_search_form": LocationSearchForm()}
        return render(self.request, "location_form.html", context)
