from Ebay import Ebay
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", context={"products": None})


@app.route("/search", methods=["POST"])
def search():
    user_search = request.form["search_input"]
    ebay = Ebay()
    all_products = ebay.search(user_search)
    avg_price = ebay.get_avg_price()
    context = {"avg_price": avg_price, "products": all_products}

    return render_template("search.html", context=context)


if __name__ == "__main__":
    app.run(debug=True)
