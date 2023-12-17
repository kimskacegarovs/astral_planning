from django.shortcuts import render, reverse, redirect, HttpResponse
from django.views.generic import TemplateView, View, FormView
from .service import PlanningService, PlanningRequest, PlanningFactory
from .models import Transport, Shipment, Location  # TODO Move to service
from .forms import LocationSearchForm, LocationForm, DeleteEntityForm
from .geo_service import GeoService
from .types import LocationSearchResult, EntityType
from django_view_decorator import view
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


@view(paths="location_search_result_select", name="location_search_result_select")
class LocationSearchResultSelectView(View):
    def post(self, request, *args, **kwargs):
        location_form_data = json.loads(self.request.POST["data"])
        result = LocationSearchResult.from_json(self.request.POST["result"])
        initial = {**location_form_data, "location": result.display_name, "coordinates": result.coordinates}
        context = {"location_form": LocationForm(initial=initial), "location_search_form": LocationSearchForm()}
        return render(self.request, "location_form.html", context)


@view(paths="location_form", name="location_form")
class LocationFormView(FormView):
    form_class = LocationForm

    def form_valid(self, form):
        lat, lng = form.cleaned_data["coordinates"].split(",")
        location = Location.objects.create(latitude=lat, longitude=lng)

        match EntityType(form.cleaned_data["entity_type"]):
            case EntityType.SHIPMENT:
                Shipment.objects.create(location=location, name=form.cleaned_data["name"])
            case EntityType.TRANSPORT:
                Transport.objects.create(location=location, name=form.cleaned_data["name"])

        return redirect("resources")


@view(paths="delete", name="delete")
class DeleteEntityView(FormView):
    form_class = DeleteEntityForm

    def form_valid(self, form):
        match EntityType(form.cleaned_data["entity_type"]):
            case EntityType.SHIPMENT:
                Shipment.objects.filter(id=form.cleaned_data["id"]).delete()
            case EntityType.TRANSPORT:
                Transport.objects.filter(id=form.cleaned_data["id"]).delete()

        return redirect("resources")