import sqlite3

'''
    Podrazumevano se transakcije automatski zapocinje i uvek postoji jedna aktivna transakcija.
    Metodom commit se izmene cuvaju u bazi, dok se metodom rollback vracamo na stanje u bazi sa pocetka transakcije.
    Obe metode pored ovoga zapocinju i novu transakciju.
    Metoda connect implicitno zapocinje novu transakciju, dok metoda close izvrsava rollback.

    Prilikom kreiranja konekcije, moguce je podesiti da se transakcije automatski izvrsavaju 
    pomocu parametra autocommit koji se postavlja na vrednost True (podrazumevano je False)
    i tada metode commit i rollback nemaju nikakve efekte. 

    Pored ovoga, u starijim verzijama Pythona postoji i parametar isolation_level.

    Detaljnije informacije o podesavanju ovih parametra mozete naci u dokumentaciji na linku:
    https://docs.python.org/3/library/sqlite3.html#sqlite3-transaction-control
'''

""" 
Zadatak - banka - dat id filijale i iznos i potrebno je da se svakom racunu koji nije obrisan oduzme iznos- odrzavanje i to tako da 
sada moze da se promeni status racuna(postane B), u stavku je potrebno dodati kao isplatu to - za redni broj staviti maksimalan redni broj za taj
racun i dodati 1

gledati sta vraca fetchall() - listu tupleova - ako je potrebno, praviti pomocni upit kroz koga cemo samo iterirati"""


def connent():
    try:
        conn = sqlite3.connect("Banka_autoincrement.db")

        return conn
    except sqlite3.Error as e:
        print(e)

def disconnent(conn):
    try:
        conn.close()
    except sqlite3.Error as e:
        print(e)


def print_all_users(conn):
    sql = "SELECT * FROM Komitent"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        print("\nAll users")
        for row in cursor.fetchall():                   #lakse uz pomoc 2 fora
            print(f"{row[0]}\t{row[1]}\t{row[2]}")
    except sqlite3.Error as e:
        print(e)

def print_all_racun(conn):
    sql = "SELECT * FROM Racun"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        print("\nSvi racuni")
        print(cursor.fetchall())
        for row in cursor.fetchall():                   #lakse uz pomoc 2 fora
            print(f"{row[0]}\t{row[1]}\t{row[2]}")
    except sqlite3.Error as e:
        print(e)


def print_all_bank_account(conn):
    sql = "SELECT * FROM Racun"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        print("\nAll bank account")
        row = cursor.fetchone()
        while row is not None:
            print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}")
            row = cursor.fetchone()
    except sqlite3.Error as e:
        print(e)

def print_all_users_with_name(conn, name):
    sql = "SELECT * FROM Komitent where Naziv = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name,))
        print(f"\nAll users with name '{name}'")
        for row in cursor.fetchall():
            print(f"{row[0]}\t{row[1]}\t{row[2]}")
    except sqlite3.Error as e:
        print(e)

def print_all_users_with_name_bad(conn, name):
    sql = f"SELECT * FROM Komitent where Naziv = '{name}'"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        print(f"\nAll users with name '{name}")
        for row in cursor.fetchall():
            print(f"{row[0]}\t{row[1]}\t{row[2]}")
    except sqlite3.Error as e:
        print(e)

def update_user_address(conn, idKom, address):
    sql = "UPDATE Komitent set Adresa = ? where idKom = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (address, idKom))
        print(f"Azurirano je {cursor.rowcount} redova")
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(e)
        return False

def insert_racun(conn, name, address):
    sql = "insert into Racun(status, idkom) values(?, ?)"
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (name, address))
            print(f"Dodat Racun sa Idrac = {cursor.lastrowid}")
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(e)
        return -1

def insert_user(conn, name, address):
    sql = "insert into Komitent(Naziv, Adresa) values(?, ?)"
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (name, address))
            print(f"Dodat Komitent sa IdKom = {cursor.lastrowid}")
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(e)
        return -1

def make_transfer_v1(conn, idRacFrom, idRacTo, iznos, error):
    sql = "update Racun set Stanje = Stanje + ? where idRac = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (-iznos, idRacFrom))
        if error:
            raise Exception("Moja greska")
        cursor.execute(sql, (iznos, idRacTo))
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

def make_transfer_v2(conn, idRacFrom, idRacTo, iznos, error):
    sql = "update Racun set Stanje = Stanje + ? where idRac = ?"
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (-iznos, idRacFrom))
            if error:
                raise Exception("Moja greska")
            cursor.execute(sql, (iznos, idRacTo))
        # with conn: omogucava da se na kraju bloka automatski automaski pozove commit() ukoliko nije doslo do greske
        # ili rollback() ukoliko dodje do greske
    except Exception as e:
        print(e)

def main():
    conn = connent()
    print_all_users(conn)
    print_all_bank_account(conn)
    print_all_users_with_name(conn, "Milica")

    update_user_address(conn, 1, "DAA")
    insert_user(conn, "Stefan", "oo")
    print_all_users(conn)

    print("Pre transakcije")
    print_all_bank_account(conn)
    make_transfer_v1(conn, 2, 1, 1000, True)
    print("Posle neuspesne transakcije")
    print_all_bank_account(conn)
    make_transfer_v1(conn, 2, 1, 100, False)
    print("Posle uspesne transakcije")
    print_all_bank_account(conn)
    print_all_racun(conn)
    insert_racun(conn, 'U', 2)
    print_all_racun(conn)
    # Umesto makeTransfer_v1 moze se pozivati i funkcija makeTransfer_v2

    '''
    # Primeri SQL Injection:
    print_all_users_with_name_bad(conn, "Milica' OR 1 = 1 --")

    # ovo ne radi zbog biblioteke, jer biblioteka za SQLite ne podrzava izvrsavanje vise upita
    print_all_users_with_name_bad(conn, "Milica'; delete from Uplata --")
    '''

    disconnent(conn)

if __name__ == '__main__':
    main()
