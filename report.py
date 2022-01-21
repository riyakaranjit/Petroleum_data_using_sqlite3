import sqlite3
from itertools import chain, islice
from collections import defaultdict

import logging

import requests


class Report:
    def __init__(self, sqlite_path='report.db'):
        self.con = sqlite3.connect(sqlite_path)
        self.cursor = self.con.cursor()
        logging.basicConfig(level=logging.DEBUG)

    def _create_tables(self):
        logging.debug("Creating tables")
        self.cursor.execute(
            "create table if not exists country (id integer primary key autoincrement, country_name text)")
        self.cursor.execute(
            "create table if not exists petroleum_product (id integer primary key autoincrement, product_name text)")
        self.cursor.execute("""
        create table if not exists petroleum_sales (
        id serial primary key,
        country_id integer, 
        product_id integer,
        year integer,
        sales float,
        foreign key(country_id) references country(id),
        foreign key(product_id) references petroleum_product(id))
        """)
        self.con.commit()
        logging.debug("Table creation complete!")

    @staticmethod
    def grouper(chunk_size, iterable):
        it = iter(iterable)
        while True:
            group = tuple(islice(it, None, chunk_size))
            if not group:
                break
            yield group

    def _populate_country_table(self, raw_data):
        """
        function to extract unique country and insert in into database
        :param raw_data: raw dict data
        :return: list of tuple containing id and country
        """
        country_names = set([(x['country'],) for x in raw_data])

        self.cursor.executemany("insert into country(country_name) values (?)", list(country_names))

        self.cursor.execute("select * from country")
        country_with_ids = self.cursor.fetchall()
        return {x[1]: x[0] for x in country_with_ids}

    def _populate_petroleum_products(self, raw_data):
        """
        function to extract unique product and insert it into database
        :param raw_data: raw dict data
        :return: list of tuple containing id and country
        """
        petroleum_products = set([(x['petroleum_product'],) for x in raw_data])

        self.cursor.executemany("insert into petroleum_product(product_name) values (?)", list(petroleum_products))

        self.cursor.execute("select * from petroleum_product")
        petroleum_product_with_ids = self.cursor.fetchall()

        return {x[1]: x[0] for x in petroleum_product_with_ids}

    def _populate_sales_data(self, sales_data):
        """#Loading the data to the database
url="https://raw.githubusercontent.com/younginnovations/internship-challenges/master/programming/petroleum-report/data.json"

def _get_data(url):
raw_data = requests.get(url)
raw_data.json()
        function to insert sales record to database
        :param sales_data: list of normalized sales data
        :return:
        """
        self.cursor.executemany("insert into petroleum_sales(country_id,product_id,year,sales) values (?,?,?,?)",
                                sales_data)

    def _load_data_from_database(self):
        """
        function to fetch all records from database
        :return:
        """
        self.cursor.execute("""
        select year, country.country_name, petroleum_product.product_name, sales 
        from petroleum_sales 
        join petroleum_product on petroleum_product.id = petroleum_sales.product_id
        join country on country.id = petroleum_sales.country_id
        """)
        return self.cursor.fetchall()

    def _print_task_iii(self):
        print(" total sale of each petroleum")
        self.cursor.execute("""select petroleum_product.product_name, sum(sales) total_sales from petroleum_sales 
                        join petroleum_product on petroleum_product.id = petroleum_sales.product_id
                        group by 1 order by 2 desc""")
        result = self.cursor.fetchall()
        print('country    total sales\n')
        for record in result:
            print(record[0] + '    ' + str(record[1]) + '\n')

    def _print_task_iv(self):
        print("top 3 countries that have the highest sales")
        self.cursor.execute("""select country.country_name, sum(sales) total_sales from petroleum_sales 
                        join country on country.id = petroleum_sales.country_id
                        group by 1 order by 2 desc limit 3""")
        result = self.cursor.fetchall()

        print('country    total sales\n')
        for record in result:
            print(record[0] + '    ' + str(record[1]) + '\n')

        print("top 3 countries that have the lowest sales")
        self.cursor.execute("""select country.country_name, sum(sales) total_sales from petroleum_sales 
                               join country on country.id = petroleum_sales.country_id
                               group by 1 order by 2 asc limit 3""")
        result = self.cursor.fetchall()

        print('country    total sales\n')
        for record in result:
            print(record[0] + '    ' + str(record[1]) + '\n')

    def _print_task_v(self):
        self.cursor.execute("""
        select year, petroleum_product.product_name, sales 
        from petroleum_sales 
        join petroleum_product on petroleum_product.id = petroleum_sales.product_id
        """)
        ress = self.cursor.fetchall()

        interval = 3
        initial_year = sorted(set([x[0] for x in ress]))

        input_dict = defaultdict(lambda: defaultdict(float))
        output_dict = defaultdict(lambda: defaultdict(list))

        for x in ress:
            input_dict[x[0]][x[1]] = x[2]

        for years in self.grouper(4, initial_year):
            first_year = years[0]
            for single_year in years:
                for product, value in input_dict[single_year].items():
                    if value != 0:
                        output_dict[first_year][product].append(value)


        formatted_string = """year       product            avg"""
        for year, product_dict in output_dict.items():
            formatted_string += "\n"
            for product, sales_list in product_dict.items():
                average_sales = sum(sales_list) / len(sales_list)
                formatted_string += str(year) + '-' + str(year + 3) + '  ' + product + '   ' + str(average_sales) + '\n'
        print(formatted_string)

    def _get_data(self, url):
        raw_data = requests.get(url)
        return raw_data.json()

    def start_process(self):
        self._create_tables()
        raw_dict = self._get_data(
            "https://raw.githubusercontent.com/younginnovations/internship-challenges/master/programming/petroleum-report/data.json")

        country_with_id = self._populate_country_table(raw_dict)
        product_with_id = self._populate_petroleum_products(raw_dict)

        normalized_sales_data = [
            (country_with_id[x['country']], product_with_id[x['petroleum_product']], x['year'], x['sale']) for x
            in raw_dict]
        self._populate_sales_data(normalized_sales_data)

        self._print_task_iii()
        self._print_task_iv()
        self._print_task_v()


if __name__ == '__main__':
    report_object = Report()
    report_object.start_process()


