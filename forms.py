from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DecimalField, StringField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from py_scripts import ACR_Globals
categories_code = ACR_Globals.__CATEGORIES
categories_name = ACR_Globals.__CATEGORIES_READABLE


class UserInsertForm(FlaskForm):
	user = IntegerField('ID', validators=[DataRequired()])
	elo = DecimalField('ELO', validators=[DataRequired()], default=8.0)
	submit = SubmitField('Crear Usuario')

class ProblemInsertForm(FlaskForm):
	problem = IntegerField('ID', validators=[DataRequired()])
	elo = DecimalField('ELO', validators=[DataRequired()], default=8.0)
	categories = SelectMultipleField('Categorias', choices = [(k, categories_name[v]) for k,v in categories_code.items()],
									validators=[DataRequired()], coerce=int)
	title = StringField('Titulo', validators=[DataRequired(), Length(min=2, max=30)])
	submit = SubmitField('Crear Problema')

class SubmissionForm(FlaskForm):
	user = IntegerField('ID del Usuario', validators=[DataRequired()])
	problem = IntegerField('ID del Problema', validators=[DataRequired()])
	language = SelectField('Lenguaje', choices = [('C','C'), ('CPP', 'CPP'), ('JAV','JAV')], validators=[DataRequired()])
	status = SelectField('Estado del Envio', choices = [('AC', 'AC'), ('WA', 'WA')], validators=[DataRequired()])
	submit = SubmitField('Enviar')

class ELOSelectionForm(FlaskForm):
	elo_type = SelectField('Tipo de ELO', choices = [(1,'Tipo 1'), (2, 'Tipo 2'), (3,'Tipo 3')], validators=[DataRequired()], coerce=int)
	submit = SubmitField('Aplicar')