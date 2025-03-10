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

class CustomUserEditForm(UserChangeForm):
    password1 = forms.CharField(
        label="Nova Senha", 
        widget=forms.PasswordInput, 
        required=False
    )
    password2 = forms.CharField(
        label="Confirme a Nova Senha", 
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "restaurante")
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "As senhas não coincidem.")
        role = cleaned_data.get("role")
        restaurante = cleaned_data.get("restaurante")
        # Validação semelhante à do formulário de criação
        if role in ["standard", "master"] and not restaurante:
            self.add_error("restaurante", "Usuários Standard e Master devem estar associados a um restaurante.")
        if role == "admin":
            cleaned_data["restaurante"] = None
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
