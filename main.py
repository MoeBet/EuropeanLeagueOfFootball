from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///stats.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db = SQLAlchemy(app)
Bootstrap(app)


class GameInfoForm(FlaskForm):
    home = SelectField('Home Team', choices=['Barcelona Dragons', 'Berlin Thunder', 'Cologne Centurions',
                                             'Frankfurt Galaxy', 'Hamburg Sea Devils', 'Leipzig Kings',
                                             'Panthers Wroclaw', 'Stuttgart Surge'], validators=[DataRequired()])
    away = SelectField('Away Team', choices=['Barcelona Dragons', 'Berlin Thunder', 'Cologne Centurions',
                                             'Frankfurt Galaxy', 'Hamburg Sea Devils', 'Leipzig Kings',
                                             'Panthers Wroclaw', 'Stuttgart Surge'], validators=[DataRequired()])
    date = DateField('Date d/m/y', format='%d/%m/%Y', validators=[DataRequired()])
    time = TimeField('Start Time', validators=[DataRequired()])
    weather = SelectField(u'Weather', choices=['Sunny', 'Windy', 'Cloudy', 'Rain', 'Heavy Rain', 'Snow'],
                          validators=[DataRequired()])
    stadium = SelectField(u'Stadium', choices=['open', 'closed'], validators=[DataRequired()])
    submit = SubmitField('Submit')


class DriveForm(FlaskForm):
    time_received = StringField('Game-Time Ball Received e.g. 14:20', validators=[DataRequired()])
    drive_began = StringField('Drive Began e.g. HSD 9', validators=[DataRequired()])
    how_ball_obtained = SelectField('How Ball Obtained', choices=['Downs', 'Fumble', 'Interception', 'Kickoff',
                                                                  'Missed FG', 'Punt'], validators=[DataRequired()])
    time_lost = StringField('Game-Time Ball Lost e.g. 14:00', validators=[DataRequired()])
    last_snap = StringField('Drive Ended e.g. HSD 45', validators=[DataRequired()])
    how_given_up = SelectField('How Ball Given Up', choices=['Downs', 'End of Game', 'Field Goal', 'Fumble', 'Interception',
                                                             'Missed FG', 'Punt', 'Touchdown'],
                               validators=[DataRequired()])
    submit = SubmitField('Submit')


class PlaysForm(FlaskForm):
    down = SelectField('Down', choices=['1', '2', '3', '4'], validators=[DataRequired()])
    yards_to_go = StringField('Yards to go', validators=[DataRequired()])
    field_pos_half = StringField('FieldPosition own or opponent half', validators=[DataRequired()])
    field_pos_yard = StringField('FieldPosition Yard', validators=[DataRequired()])
    time = StringField('Gametime', validators=[DataRequired()])
    shotgun = StringField('Shotgun Formation', validators=[DataRequired()])
    play_description = StringField('Play description e.g. S.Darnold pass incomplete deep right to C.Herndon.', validators=[DataRequired()])
    submit = SubmitField('Submit')


class GameInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home = db.Column(db.String, nullable=False)
    away = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    weather = db.Column(db.String, nullable=False)
    stadium = db.Column(db.String, nullable=False)


class OverallDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_received = db.Column(db.String, nullable=True)
    how_ball_obtained = db.Column(db.String, nullable=True)
    time_lost = db.Column(db.String, nullable=True)
    drive_began = db.Column(db.String, nullable=True)
    last_snap = db.Column(db.String, nullable=True)
    how_given_up = db.Column(db.String, nullable=True)


class Plays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    down = db.Column(db.String, nullable=False)
    yards_to_go = db.Column(db.String, nullable=False)
    field_pos_half = db.Column(db.String, nullable=False)
    field_pos_yard = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    shotgun = db.Column(db.String, nullable=False)
    play_description = db.Column(db.String(250), nullable=True)


db.create_all()


@app.route('/')
def home():
    game_info = db.session.query(GameInfo).all()
    overall_drive = db.session.query(OverallDrive).all()
    plays = db.session.query(Plays).all()
    return render_template("index.html", game_info=game_info, overall_drive=overall_drive, plays=plays)


@app.route("/addgame", methods=['GET', 'POST'])
def add():
    form = GameInfoForm()
    if request.method == 'POST':
        new_game = GameInfo(
                            home=request.form["home"],
                            away=request.form["away"],
                            date=request.form["date"],
                            time=request.form["time"],
                            weather=request.form["weather"],
                            stadium=request.form["stadium"]
                            )
        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("addgame.html", form=form)


@app.route("/drive", methods=['GET', 'POST'])
def add_drive():
    form = DriveForm()
    if request.method == 'POST':
        new_drive = OverallDrive(
                                 time_received=request.form["time_received"],
                                 how_ball_obtained=request.form["how_ball_obtained"],
                                 time_lost=request.form["time_lost"],
                                 drive_began=request.form["drive_began"],
                                 last_snap=request.form["last_snap"],
                                 how_given_up=request.form["how_given_up"],
                                 )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("adddrive.html", form=form)

@app.route("/play", methods=['GET', 'POST'])
def playbyplay():
    form = PlaysForm()
    if request.method == 'POST':
        new_play = Plays(
                         down=request.form["down"],
                         yards_to_go=request.form["yards_to_go"],
                         field_pos_half=request.form["field_pos_half"],
                         field_pos_yard=request.form["field_pos_yard"],
                         time=request.form["time"],
                         shotgun=request.form["shotgun"],
                         play_description=request.form["play_description"],
                         )
        db.session.add(new_play)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("addplay.html", form=form)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        book_id = request.form['id']
        book_to_update = Books.query.get(book_id)
        book_to_update.rating = request.form['rating']
        db.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = Books.query.get(book_id)
    return render_template("edit.html", book=book_selected)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    book_id = request.args.get('id')
    book_to_delete = Books.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
