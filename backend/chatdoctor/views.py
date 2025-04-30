from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import (
    get_symptom_matches, predict_disease, get_related_symptoms,
    second_prediction, calc_condition, description_dict, precaution_dict, initialize, cols
)

def index(request):
    return render(request, 'chatdoctor/index.html')

from django.http import JsonResponse

from django.http import JsonResponse
from .utils import calc_condition, second_prediction, initialize  # Ensure to import your actual functions



def process_diagnosis(request):
    initialize()
    if request.method == 'POST':
        symptom = request.POST.get('selected_symptom')
        days = int(request.POST.get('days', 0))
        additional_symptoms = request.POST.getlist('additional_symptoms', [])
        if not symptom or days <= 0:
            return JsonResponse({'error': 'Invalid symptom or days.'}, status=400)
        present_disease = predict_disease(symptom)
        symptoms_exp = [symptom] + additional_symptoms
        second_pred = second_prediction(symptoms_exp)
        severity = calc_condition(symptoms_exp, days)
        result = {
            'severity': severity,
            'symptoms': symptoms_exp,
            'disease': present_disease,
            'description': description_dict.get(present_disease, 'No description available.'),
            'precautions': precaution_dict.get(present_disease, []),
            'second_disease': second_pred if second_pred != present_disease else None,
            'second_description': description_dict.get(second_pred, 'No description available.') if second_pred != present_disease else None
        }
        return JsonResponse(result)
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def get_additional_symptoms(request):
    try:
        initialize()
        if request.method == 'POST':
            symptom = request.POST.get('selected_symptom')
            if not symptom:
                return JsonResponse({'error': 'No symptom provided.'}, status=400)
            
            disease = predict_disease(symptom)
            if not disease:
                return JsonResponse({'error': 'Could not predict disease from symptom.'}, status=400)
            
            symptoms = get_related_symptoms(disease)
            if not symptoms:
                return JsonResponse({'additional_symptoms': []})
                
            # Filter out the main symptom
            symptoms = [s for s in symptoms if s != symptom]
            return JsonResponse({'additional_symptoms': symptoms})
            
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    except Exception as e:
        print(f"Error in get_additional_symptoms: {str(e)}")
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def process_symptom(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST method required'}, status=400)
            
        symptom = request.POST.get('symptom')
        if not symptom:
            return JsonResponse({'error': 'Symptom parameter missing'}, status=400)
        
        matches = get_symptom_matches(symptom)
        
        if not matches:
            return JsonResponse({'error': 'No matching symptoms found'}, status=404)
            
        return JsonResponse({'matches': matches})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    







class RegisterView(APIView):
    def post(self, request):
        email= request.data.get('email')
        username = request.data.get('username') or email.split('@')[0]
        password = request.data.get("password")

        if User.objects.filter(email=email).exists():
            return Response({ "error": "User not found" }, status=400)
        
        user = User.objects.create_user(username=username, password=password,email=email)
        return Response({"message": "User created"}, status=201)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=401)
        
        user = authenticate(username=user.username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "id": user.id,
                "username": user.username,
                "email": user.email
            })
        return Response({"error": "Invalid credentials"}, status=401)
    