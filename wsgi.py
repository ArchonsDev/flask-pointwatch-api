from api import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    import platform

    if platform.system() == 'Windows':
        from api import socketio

        socketio.run(app, debug=True)
    else:
        worker_class = 'gevent'

        options = {
            'bind': '0.0.0.0:8000',
            'workers': 4,
            'worker_class': 'gevent',
            'accesslog': '-',
            'errorlog': '-'
        }

        # Run the application with Gunicorn
        from gunicorn.app.wsgiapp import WSGIApplication
        WSGIApplication("%(prog)s [OPTIONS]").run()
