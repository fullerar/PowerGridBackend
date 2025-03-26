# main.py (formerly app.py)
from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
from schema import schema

app = Flask(__name__)
CORS(app)

# Add GraphQL endpoint with POST + GET support
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    ),
    methods=['GET', 'POST']
)

# Optional home route
@app.route('/')
def home():
    return "<h2>Welcome — go to <a href='/graphql'>/graphql</a> to explore the API</h2>"

if __name__ == '__main__':
    app.run(debug=True)
