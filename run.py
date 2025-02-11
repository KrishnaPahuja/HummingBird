from main import app # if main is package (which it is) then it will check for app in __init__ file

if __name__ == '__main__':
    app.run(debug=True)
