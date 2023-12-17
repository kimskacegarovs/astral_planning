from django.shortcuts import render, reverse, redirect, HttpResponse
from django.views.generic import TemplateView, View, FormView
from .service import PlanningService, PlanningRequest
from .models import Transport, Shipment, Location  # TODO Move to service
from .forms import LocationSearchForm, LocationForm, DeleteEntityForm
from .geo_service import GeoService
from .types import LocationSearchResult, EntityType
from django_view_decorator import view
from utils import Timer
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
        planning_set = PlanningService().get_planning_set()
        context["planning_set"] = planning_set
        context["planning_polylines"] = PlanningService().get_planning_polylines(planning_set)
        return context


class ApplyPlanningView(View):
    def post(self, request, *args, **kwargs):
        planning_request = PlanningRequest(**json.loads(self.request.POST["planning_request"]))
        PlanningService().apply_planning(planning_request=planning_request)
        return redirect("resources")


@view(paths="reset_planning", name="reset_planning")
class ResetPlanningView(View):
    def post(self, request, *args, **kwargs):
        PlanningService().reset_planning()
        return redirect("resources")


@view(paths="cancel_planning", name="cancel_planning")
class CancelPlanningView(View):
    def post(self, request, *args, **kwargs):
        PlanningService().cancel_planning(planning_id=self.request.POST["planning_id"])
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
        initial = {**location_form_data, "address": result.display_name, "coordinates": result.coordinates}
        context = {"location_form": LocationForm(initial=initial), "location_search_form": LocationSearchForm()}
        return render(self.request, "location_form.html", context)


@view(paths="location_form", name="location_form")
class LocationFormView(FormView):
    form_class = LocationForm

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        lat, lng = form.cleaned_data["coordinates"].split(",")
        location = Location.objects.create(latitude=lat, longitude=lng, address=form.cleaned_data["address"])

        match EntityType(form.cleaned_data["entity_type"]):
            case EntityType.SHIPMENT:
                Shipment.objects.create(location=location, name=name)
            case EntityType.TRANSPORT:
                Transport.objects.create(location=location, name=name)

        return redirect("resources")

    def form_invalid(self, form):
        # TODO Figure out how to handle invalid form
        return HttpResponse("Invalid form")


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


@view(paths="apply_optimised_planning", name="apply_optimised_planning")
class ApplyOptimisedPlanningView(View):
    def post(self, request, *args, **kwargs):
        with Timer(method=self.post.__qualname__):
            PlanningService().apply_optimal_planning()
            return redirect("resources")


@view(paths="request_route", name="request_route")
class RequestRouteView(View):
    def post(self, request, *args, **kwargs):
        planning_id = self.request.POST["planning_id"]
        PlanningService().request_route(planning_id=planning_id)
        return redirect("resources")
