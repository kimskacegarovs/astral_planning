import json

from django.shortcuts import HttpResponse, redirect, render, reverse
from django.views.generic import FormView, TemplateView, View
from django_view_decorator import view
from utils import timer

from .forms import CreateEntityForm, DeleteEntityForm, LocationSearchForm, OptimisePlanningForm
from .geo_service import GeoService
from .models import Location, Shipment, Transport
from .service import PlanningRequest, PlanningService
from .types import EntityType, LocationSearchResult


class PlanningView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apply_planning_url"] = reverse("apply_planning")
        context["location_form"] = CreateEntityForm()
        context["location_search_form"] = LocationSearchForm()
        return context


class ResourcesView(TemplateView):
    template_name = "resources.html"

    @timer()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apply_optimised_planning = self.request.session.get("apply_optimised_planning", False)
        planning_set = PlanningService().get_planning_set()

        if apply_optimised_planning:
            if not planning_set.plannings.filter(route__isnull=True):
                print("Received all routes. Applying optimal planning.")
                PlanningService().reset_planning()
                PlanningService().apply_optimal_planning()
                self.request.session["apply_optimised_planning"] = False

        context["planning_set"] = planning_set
        context["planning_polylines"] = PlanningService().get_planning_polylines(planning_set)
        context["optimise_planning_form"] = OptimisePlanningForm()
        return context


class ApplyPlanningView(View):
    @timer()
    def post(self, request, *args, **kwargs):
        planning_request = PlanningRequest(**json.loads(self.request.POST["planning_request"]))
        PlanningService().apply_planning(planning_request=planning_request)
        return redirect("resources")


@view(paths="reset_planning", name="reset_planning")
class ResetPlanningView(View):
    @timer()
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

    @timer()
    def form_valid(self, form):
        search_results = GeoService().search(search=form.cleaned_data["search"])
        return render(self.request, "location_search_results.html", {"search_results": search_results})


@view(paths="location_search_result_select", name="location_search_result_select")
class LocationSearchResultSelectView(View):
    def post(self, request, *args, **kwargs):
        location_form_data = json.loads(self.request.POST["data"])
        result = LocationSearchResult.from_json(self.request.POST["result"])
        initial = {**location_form_data, "address": result.display_name, "coordinates": result.coordinates}
        context = {"location_form": CreateEntityForm(initial=initial), "location_search_form": LocationSearchForm()}
        return render(self.request, "location_form.html", context)


@view(paths="create_entity", name="create_entity")
class CreateEntityView(FormView):
    form_class = CreateEntityForm

    @timer()
    def form_valid(self, form):
        name = form.cleaned_data["name"]
        lat, lng = form.cleaned_data["coordinates"].split(",")
        location, _ = Location.objects.get_or_create(latitude=lat, longitude=lng, address=form.cleaned_data["address"])
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
    @timer()
    def post(self, request, *args, **kwargs):
        self.request.session["apply_optimised_planning"] = True
        max_empty_km = int(self.request.POST["max_empty_km"]) if self.request.POST["max_empty_km"] else None
        PlanningService().apply_optimal_planning(max_empty_km=max_empty_km)
        return redirect("resources")


@view(paths="request_route", name="request_route")
class RequestRouteView(View):
    @timer()
    def post(self, request, *args, **kwargs):
        planning_id = self.request.POST["planning_id"]
        PlanningService().request_route(planning_id=planning_id)
        return redirect("resources")
