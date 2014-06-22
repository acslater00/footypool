from footy import make_application

if __name__ == '__main__':
    app = make_application('development')
    app.run(debug=True, host='0.0.0.0', port=app.config['PORT'])
