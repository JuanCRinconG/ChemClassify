from LogicaMadre.ConstructorClasesGlobales.InstanciasPrincipales import PlataformaWeb, db

def main():
    if db:
        print('ok')
    PlataformaWeb.run(debug=True)

if __name__ == '__main__':
    main()