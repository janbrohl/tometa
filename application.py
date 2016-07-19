from tometa import App

application = App()

if __name__ == "__main__":
    import wsgiref.simple_server
    serv = wsgiref.simple_server.make_server("localhost", 8080, application)
    serv.serve_forever()
