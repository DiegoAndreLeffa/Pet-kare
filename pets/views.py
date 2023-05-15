from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView, Request, Response, status
from .serializers import PetSerializer
from .models import Pet
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetViews(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:

        trait = request.query_params.get("trait", None)

        if trait:
            pets = Pet.objects.filter(traits__name=trait)
            result_page = self.paginate_queryset(pets, request)

            serializer = PetSerializer(result_page, many=True)

            return self.get_paginated_response(serializer.data)

        pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits")

        group_dict = Group.objects.filter(
            scientific_name__iexact=group["scientific_name"]
        ).first()
        if not group_dict:
            group_dict = Group.objects.create(**group)

        pet_object = Pet.objects.create(**serializer.validated_data, group=group_dict)

        for trait in traits:
            trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait)

            pet_object.traits.add(trait_obj)

        serializer = PetSerializer(pet_object)

        return Response(serializer.data, status.HTTP_201_CREATED)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group_data: dict = serializer.validated_data.pop("group", None)

        if group_data:
            try:
                group = Group.objects.get(scientific_name=group_data["scientific_name"])
                pet.group = group
                pet.save()
            except Group.DoesNotExist:
                group_dict = Group.objects.create(**group_data)
                pet.group = group_dict
                pet.save()

        traits_data: list = serializer.validated_data.pop("traits", None)

        if traits_data:
            # pet.traits.delete()
            for trait in traits_data:

                trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait)

                pet.traits.add(trait_obj)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
