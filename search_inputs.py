def get_user_input():
    query = input("Spécialité recherchée (ex: dermatologue) : ")
    max_results = int(input("Nombre max de résultats (défaut: 10) : ") or 10)
    sector = input("Secteur (1, 2, non-conventionné) : ")
    address_keyword = input("Mot-clé dans l'adresse (ex: '75015') : ")

    return locals()