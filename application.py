from flask import Flask, jsonify, request, render_template, url_for
from elasticsearch import Elasticsearch
from elasticsearch.connection import create_ssl_context
import ssl
import requests
import json

# from datetime import datetime
# from bson.json_util import dumps
# from json import loads

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

context = create_ssl_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

es = Elasticsearch(
['ca98ff291d2d43b0b4b58d6690388e2d.eastus2.azure.elastic-cloud.com'],
http_auth=('elastic', 'G05ZW6nzrSsKsByMfdwYzrDn'),
scheme="https",
port=9243,
ssl_context = context,
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/results/", methods=['POST'])
def result():
	text = request.form['text']
	url_api = 'https://imdbrecommender.azurewebsites.net/search/?text=' + text + '\''
	r = requests.get(url_api) 
	query_results = json.loads(r.text)['hits']
	return render_template("results.html", q_exact=query_results, q_desc=query_results, q_genre=query_results, q_writer=query_results)

@app.route('/search/', methods=['GET','POST'])
def search():
    text = request.args.get('text', '')
    yeargte = request.args.get('yeargte', '')
    yearlte = request.args.get('yearlte', 2020)
    avg_vote = request.args.get('avg_vote', '')
    genre = request.args.get('genre', '')
    country = request.args.get('country', '')
    language = request.args.get('language', '')



    query = {
    "from" : 0, "size" : 30,
    "query": {
        "bool": {
            "should": [],
            "filter": [{
                "bool": {
                    "must": []
                }
            }
            ]
            }
        }
    }

    if text:
        text = [
              { "match": { "original_title": {"query": text, "boost": 4 }}},
              { "match": { "director": {"query": text, "boost": 3 }}},
              { "match": { "actors": {"query": text, "boost": 3 }}},
              { "match": { "genre": {"query": text, "boost": 2 }}},
              { "match": { "country": {"query": text, "boost": 1 }}},
              { "match": { "language": {"query": text, "boost": 1 }}},
              { "match": { "writer": {"query": text, "boost": 1 }}},
              { "match": { "production_company": {"query": text, "boost": 1 }}},
              { "match": { "description": {"query": text, "boost": 1 }}}
              ]
        query["query"]["bool"]["should"].extend(text)
    if yeargte:
        year = {"range": { "year": { "gte": yeargte, "lte": yearlte}}}
        query["query"]["bool"]["filter"].append(year)
    if avg_vote:
        avg_vote = {"range": { "avg_vote": { "gte": avg_vote }}}
        query["query"]["bool"]["filter"].append(avg_vote)
    if genre:
        genre = {"match": {"genre": {"query": genre}}}
        query["query"]["bool"]["filter"][0]["bool"]["must"].append(genre)
    if country:
        country = {"match": {"country": {"query": country}}}
        query["query"]["bool"]["filter"][0]["bool"]["must"].append(country)
    if language:
        language = {"match": {"language": {"query": language}}}
        query["query"]["bool"]["filter"][0]["bool"]["must"].append(language)

    print(query)
    res = es.search(index="",body=query)

    try:
        print("%d Entries:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print(hit["_score"])
            print("%(avg_vote)s: %(original_title)s (%(year)s)" % hit["_source"])
    except:
        res = es.search(index="faf42_movies1",body=query)
    return res

if __name__ == '__main__':
    app.run(debug=True)
