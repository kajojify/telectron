import sqlite3


class SQLiter:
    def __init__(self, database='test.db'):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def create_route(self, user_id, country, dep_region, arr_region,
                     dep_station, arr_station, dep_code, arr_code):
        with self.connection:
            self.cursor.execute("INSERT INTO countries (user, country, dep_region, arr_region, dep_station, arr_station, dep_code, arr_code) "
                                "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}');".format(user_id, country, dep_region, arr_region,
                     dep_station, arr_station, dep_code, arr_code))




    def write_country(self, user_id, country):
        with self.connection:
            self.cursor.execute("INSERT INTO countries (user, country) VALUES ('{0}', '{1}');".format(user_id, country))

    def get_user_country(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT country FROM countries WHERE user='{0}'".format(user_id)).fetchone()[0]

    def get_user_arr_station(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT arr_station FROM countries WHERE user='{0}'".format(user_id)).fetchone()[0]

    def get_user_dep_station(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT dep_station FROM countries WHERE user='{0}'".format(user_id)).fetchone()[0]

    def write_dep_region(self, user_id, region):
        with self.connection:
            self.cursor.execute("UPDATE countries SET dep_region='{0}' WHERE user='{1}';".format(region, user_id))

    def write_arr_region(self, user_id, region):
        with self.connection:
            self.cursor.execute("UPDATE countries SET arr_region='{0}' WHERE user='{1}';".format(region, user_id))

    def write_arr_station(self, user_id, station):
        with self.connection:
            self.cursor.execute("UPDATE countries SET arr_station='{0}' WHERE user='{1}';".format(station, user_id))


    def write_arrcode_station(self, user_id, station):
        with self.connection:
            self.cursor.execute("UPDATE countries SET arrcode='{0}' WHERE user='{1}';".format(station, user_id))


    def write_depcode_station(self, user_id, station):
        with self.connection:
            self.cursor.execute("UPDATE countries SET depcode='{0}' WHERE user='{1}';".format(station, user_id))


    def get_user_depcode_station(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT depcode FROM countries WHERE user='{0}'".format(user_id)).fetchone()[0]

    def get_user_arrcode_station(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT arrcode FROM countries WHERE user='{0}'".format(user_id)).fetchone()[0]


    def write_dep_station(self, user_id, station):
        with self.connection:
            self.cursor.execute("UPDATE countries SET dep_station='{0}' WHERE user='{1}';".format(station, user_id))

    def select_all(self, user_id):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM countries WHERE user="{0}"'.format(user_id)).fetchall()


    def has_country(self, user_id):
        self.cursor.execute('SELECT * FROM countries WHERE user={0}'.format(user_id))
        return bool(self.cursor.fetchall())



    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()