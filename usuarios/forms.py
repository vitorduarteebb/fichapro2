from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "restaurante")
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        restaurante = cleaned_data.get("restaurante")
        # Usuários Standard e Master devem ter restaurante vinculado
        if role in ["standard", "master"] and not restaurante:
            self.add_error("restaurante", "Usuários Standard e Master devem estar associados a um restaurante.")
        # Usuários Admin não devem ter restaurante associado
        if role == "admin":
            cleaned_data["restaurante"] = None
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "restaurante")
