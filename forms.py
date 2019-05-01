from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DecimalField, StringField
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
