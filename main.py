from flask import Flask
from birleştir import second
from birleştir import second1

app = Flask(__name__)
app.register_blueprint(second)
app.register_blueprint(second1)

@app.route("/")
def ana_sayfa():
    return """
<h1 style="text-align: center;">ana sayfa</h1>
<br>
<style>
form{
    text-align: center;
}
</style>
<form action="/register" method="get">
    <input type="submit" value="kayıt ol">
</form>
<br>
<form action="/login" method="get">
    <input type="submit" value="şifreni öğren">
</form>
"""
if __name__ == "__main__":
    app.run(debug=True)
