# using python 3
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators
from data import ACTORS
import glob
import ras_parser
# import yaml

app = Flask(__name__)
# Flask-WTF requires an enryption key - the string can be anything
# API key put in a separate file
# with open('api-key.yaml', 'r') as stream:
#      api_keys = yaml.safe_load(stream)

# print (api_keys)

app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
# Flask-Bootstrap requires this line
Bootstrap(app)
# this turns file-serving to static, using Bootstrap files installed in env
# instead of using a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    name = StringField('Local RAS project directory:', validators=[validators.DataRequired()])
    name_submit = SubmitField('Submit')

    shp = StringField('RAS Model Boundary Shapefile: \
        *Note: Extracting a RAS Feature to a Shapefile can be done from RAS Mapper.', validators=[validators.DataRequired()])
    shp_submit = SubmitField('Submit')

# define functions to be used by the routes (just one here)

# retrieve all the names from the dataset and put them into a list
def get_names(source):
    names = []
    for row in source:
        name = row["name"]
        names.append(name)
    return sorted(names)

# all Flask routes below

# two decorators using the same function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    # names = get_names(ACTORS)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        print ('\n' + form.name.data + '\n')
        prj_files = glob.glob(rf'{form.name.data}')
        print (f'\n{*prj_files,}\n')
        if len(prj_files) > 0:
            message = f"RAS project file found:\n {*prj_files,}"
            # parse prj file
            ras_parser.parse(prj_files[0])
        elif len(prj_files) == 0:
            message = "No *.prj files found. Ensure directory contains a RAS project."
        elif len(prj_files) > 1:
            message = "Multiple *.prj files found. Ensure directory contains a single RAS project in the specified directory.\
                \n project files found:\n {*prj_files,}"
        # empty the form field
        # form.name.data = ""
    # notice that we don't need to pass name or names to the template
    return render_template('index.html', form=form, message=message)

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
