from flask_wtf import FlaskForm
from wtforms import (
    Form,
    HiddenField,
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    TextAreaField,
    IntegerField,
    DateField,
    BooleanField,
    DecimalField,
    FieldList,
    FormField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    NumberRange,
    Optional
)
from models import Customer, MenuItem, MenuItemCategoryEnum
from datetime import date

class EarningsReportFilterForm(FlaskForm):
    # Disable CSRF protection for this form
    class Meta:
        csrf = False
    
    postal_code = StringField('Postal Code', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'All'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[Optional()])
    min_age = IntegerField('Minimum Age', validators=[Optional(), NumberRange(min=0)])
    max_age = IntegerField('Maximum Age', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Apply Filters')
    
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    gender = SelectField(
        'Gender',
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        validators=[DataRequired()]
    )
    birthdate = DateField('Birthdate', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=9, max=15)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=4, max=5)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')]
    )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = Customer.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderItemForm(Form):
    menu_item_id = SelectField('Menu Item', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    id = HiddenField('id')

class OrderForm(FlaskForm):
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    discount_code = StringField('Discount Code')
    submit = SubmitField('Place Order')

    def validate(self, *args, **kwargs):
        # First, run the default validations
        if not super().validate(*args, **kwargs):
            return False

        # Check if at least one item is a Pizza
        has_pizza = False
        for item_form in self.items:
            menu_item = MenuItem.query.get(item_form.menu_item_id.data)
            if menu_item and menu_item.category == MenuItemCategoryEnum.Pizza:
                has_pizza = True
                break

        if not has_pizza:
            self.items.errors.append('You must order at least one Pizza.')
            return False

        return True