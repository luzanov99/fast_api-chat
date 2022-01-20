from starlette_wtf import StarletteForm
from wtforms import StringField, BooleanField, EmailField, PasswordField
from wtforms.validators	import DataRequired, Email

class RegisterUserForm(StarletteForm):
    name = StringField('name', validators=[DataRequired()])
    admin= BooleanField('admin')
    email=EmailField('email', validators=[Email()])
    password=PasswordField()


    def is_admin(self):
        if self.admin==True:
            return True
        else:
            return False
    


class LoginUserForm(StarletteForm):
    login=StringField('login', validators=[DataRequired()])
    password=PasswordField()


    