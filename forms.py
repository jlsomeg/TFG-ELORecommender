from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DecimalField, StringField, SelectField
from wtforms.validators import DataRequired, Length


class UserInsertForm(FlaskForm):
	user = IntegerField('ID', validators=[DataRequired()])
	elo = DecimalField('ELO', validators=[DataRequired()], default=8.0)
	submit = SubmitField('Crear Usuario')

class ProblemInsertForm(FlaskForm):
	problem = IntegerField('ID', validators=[DataRequired()])
	elo = DecimalField('ELO', validators=[DataRequired()], default=8.0)
	title = StringField('Titulo', validators=[DataRequired(), Length(min=2, max=30)])
	submit = SubmitField('Crear Problema')

class SubmissionForm(FlaskForm):
	user = IntegerField('ID del Usuario', validators=[DataRequired()])
	problem = IntegerField('ID del Problema', validators=[DataRequired()])
	language = SelectField('Lenguaje', choices = [('C','C'), ('CPP', 'CPP'), ('JAV','JAV')], validators=[DataRequired()])
	status = SelectField('Estado del Envio', choices = [('AC', 'AC'), ('WA', 'WA')], validators=[DataRequired()])
	submit = SubmitField('Enviar')
