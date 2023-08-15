import psycopg2

class ClientsDB:
    def __init__(self, cursor, connect):
        self.cursor = cursor
        self.connect = connect
        
    def create_db_structure(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            surname VARCHAR(40) NOT NULL,
            email VARCHAR(80)
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS phones(
            client_id INTEGER NOT NULL REFERENCES clients(client_id),
            phone VARCHAR(15) UNIQUE
            );
        """)

        self.connect.commit()

    def add_client(self, name, surname, email, phones=None):
        self.cursor.execute("""
            INSERT INTO clients(name, surname, email) 
            VALUES(%s, %s, %s) RETURNING client_id;
        """, (name, surname, email))
        client_id = self.cursor.fetchone()[0]

        if phones:
            for phone in phones:
                self.cursor.execute("""
                    INSERT INTO phones(phone, client_id) VALUES(%s, %s);
                """, (phone, client_id))
            
        self.connect.commit()

    def add_phone(self, client_id, phone):
        self.cursor.execute("""
            INSERT INTO phones(phone, client_id) VALUES(%s, %s);
        """, (phone, client_id))

        self.connect.commit()

    def change_client_info(self, client_id, name=None, surname=None, email=None, phone=None):
        if name:
            self.cursor.execute("""
                UPDATE clients
                    SET name = %s
                    WHERE client_id = %s;
            """, (name, client_id))

        if surname:
            self.cursor.execute("""
                UPDATE clients
                    SET surname = %s
                    WHERE client_id = %s;
            """, (surname, client_id))

        if email:
            self.cursor.execute("""
                UPDATE clients
                    SET email = %s
                    WHERE client_id = %s;
            """, (email, client_id))

        if phone:
            self.cursor.execute("""
                UPDATE phones
                    SET phone = %s
                    WHERE client_id = %s;
            """, (phone, client_id))

        self.connect.commit()

    def delete_phone(self, client_id, phone):
        self.cursor.execute("""
            DELETE FROM phones
                WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))

        self.connect.commit()

    def delete_client(self, client_id):
        self.cursor.execute("""
            DELETE FROM phones
                WHERE client_id = %s;
        """, (client_id,))
        
        self.cursor.execute("""
            DELETE FROM clients
                WHERE client_id = %s;
        """, (client_id,))

        self.connect.commit()

    def find_client(self, name=None, surname=None, email=None, phone=None):
        results = []
        if name:
            self.cursor.execute("""
                SELECT client_id, name, surname, email FROM clients
                WHERE name=%s;
            """, (name,))
            results.append(set(self.cursor.fetchall()))

        if surname:
            self.cursor.execute("""
                SELECT client_id, name, surname, email FROM clients
                WHERE surname=%s;
            """, (surname,))
            results.append(set(self.cursor.fetchall()))

        if email:
            self.cursor.execute("""
                SELECT client_id, name, surname, email FROM clients
                WHERE email=%s;
            """, (email,))
            results.append(set(self.cursor.fetchall()))

        if phone:
            self.cursor.execute("""
                SELECT client_id, phone FROM phones
                WHERE phone=%s;
            """, (phone,))
            phone_res = self.cursor.fetchone()
            
            if phone_res:
                self.cursor.execute("""
                    SELECT client_id, name, surname, email FROM clients
                    WHERE client_id=%s;
                """, (phone_res[0],))
                results.append(set(self.cursor.fetchall()))
            else:
                results = [set()]
          
        if results == [set()]:
            print("No client found\n")
        else:
            res_intersec = results[0]
            for result in results[1:]:
                res_intersec &= result
            res_intersec = list(res_intersec)

            for person in res_intersec:
                out = []
                for field in person:
                    out.append(field)

                self.cursor.execute("""
                    SELECT phone FROM phones
                    WHERE client_id=%s;
                """, (out[0],))
                client_phones = self.cursor.fetchall()
                for phone_tuple in client_phones:
                    for phone in phone_tuple:
                        out.append(phone)

                for field in out:
                    print(field)
                print()
            
def main():
    conn = psycopg2.connect(database="clients_db", user="postgres", password="")
    with conn.cursor() as cur:
        clients = ClientsDB(cur, conn)
        clients.create_db_structure()

        clients.add_client('Boris', 'Nefedov', 'bornefed67@write.org', ['+79534898123', '+74959956348'])
        clients.add_client('Maria', 'Barabanova', 'marbarara99@pismo.net')
        clients.add_client('Boris', 'Petrov', 'petrbor444@letmail.org')
        clients.add_client('Alexey', 'Petrov', 'petralex_22@pismo.net', ['+79845323457'])
        clients.add_client('Elena', 'Resnichenko', 'lena_resnica562@write.org', ['+79226067314'])
        clients.add_client('Karina', 'Nemchinova', 'karnem23karnem@letmail.org', ['+79073382299'])
        clients.add_phone(1, '+79611926348')
        clients.add_phone(2, '+79123445216')

        clients.delete_phone(1, '+79534898123')

        clients.delete_client(2)

        clients.find_client(name='Boris')
        clients.find_client(surname='Petrov')
        clients.find_client(email='karnem23karnem@letmail.org')
        clients.find_client(phone='+79226067314')

        clients.change_client_info(5, name='Irina', surname='Krasnova', email='redirina@topmail.com', phone='+79412347565')
        clients.find_client(name='Irina')

    conn.close()

if __name__ == "__main__":
    main()