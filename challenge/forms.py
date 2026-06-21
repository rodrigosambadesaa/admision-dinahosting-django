from django import forms

from .services import InputSanitizationError, parse_range_boundary, sanitize_range_input


class FibonacciForm(forms.Form):
    start_date = forms.CharField(
        label="Fecha de inicio (UTC)",
        max_length=256,
        widget=forms.TextInput(
            attrs={
                "placeholder": "2026-06-01 00:00:00 o ts:12345678901234567890",
                "spellcheck": "false",
                "autocapitalize": "off",
                "autocomplete": "off",
            }
        ),
    )
    end_date = forms.CharField(
        label="Fecha de fin (UTC)",
        max_length=256,
        widget=forms.TextInput(
            attrs={
                "placeholder": "2026-06-30 23:59:59 o ts:12345678901234567999",
                "spellcheck": "false",
                "autocapitalize": "off",
                "autocomplete": "off",
            }
        ),
    )

    def clean_start_date(self) -> str:
        return self._sanitize("start_date")

    def clean_end_date(self) -> str:
        return self._sanitize("end_date")

    def _sanitize(self, field_name: str) -> str:
        value = self.cleaned_data[field_name]

        try:
            sanitized = sanitize_range_input(value)
            parse_range_boundary(sanitized)
            return sanitized
        except InputSanitizationError as exc:
            raise forms.ValidationError(str(exc)) from exc
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc


class LoginForm(forms.Form):
    usuario = forms.EmailField(
        label="Usuario",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "nombre@dominio.com",
                "autocomplete": "username",
                "class": "form-control form-control-lg",
            }
        ),
    )
    contrasena = forms.CharField(
        label="Contraseña",
        min_length=8,
        max_length=64,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "pattern": "(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9]{8,64}",
                "inputmode": "text",
                "minlength": "8",
                "maxlength": "64",
                "class": "form-control form-control-lg",
            }
        ),
        help_text="Mínimo 8 caracteres, al menos una mayúscula, una minúscula y sin caracteres especiales.",
    )
    recordar_contrasena = forms.BooleanField(
        label="Recordar contraseña",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
