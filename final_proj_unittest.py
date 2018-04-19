import sqlite3
import unittest
import final_proj_4_14 as proj

class TestTables(unittest.TestCase):

    def testRestaurant(self):
        try:
            conn = sqlite3.connect('food_event.db')
            cur = conn.cursor()
        except Error as e:
            print(e)

        sql1 = '''
        SELECT COUNT(*), city
        FROM Restaurants
        '''
        results = cur.execute(sql1)
        result_lst = results.fetchall()

        sql2 = '''
        SELECT COUNT(*), state
        FROM Restaurants
        '''
        results2 = cur.execute(sql2)
        result_lst2 = results.fetchall()

        sql3 = '''
        SELECT city
        FROM Restaurants
        '''
        results3 = cur.execute(sql3)
        result_lst3 = results.fetchall()

        self.assertGreater(result_lst[0][0], 50)
        self.assertIs(type(result_lst[0][1]), str)
        self.assertIs(len(result_lst2[0][1]), 2)
        self.assertIn(('San Francisco',), result_lst3)
        self.assertGreater(len(result_lst3),100)


    def testEvents(self):
        try:
            conn = sqlite3.connect('food_event.db')
            cur = conn.cursor()
        except Error as e:
            print(e)

        sql1 = '''
        SELECT PostalCode, city, state
        FROM Events
        '''

        results = cur.execute(sql1)
        result_lst = results.fetchall()

        self.assertIs(len(result_lst[0][2]), 2)
        self.assertIs(type(result_lst[0][1]), str)
        self.assertGreater(len(result_lst), 100)
        self.assertIs(type(result_lst[0]), tuple)
        self.assertIs(type(result_lst[0][0]), str)

    def testPostalCodes(self):
        try:
            conn = sqlite3.connect('food_event.db')
            cur = conn.cursor()
        except Error as e:
            print(e)

        sql1 = '''
        SELECT PostalCode
        FROM PostalCodes
        '''

        results = cur.execute(sql1)
        result_lst = results.fetchall()

        sql2 = '''
        SELECT Id
        FROM PostalCodes
        '''

        results2 = cur.execute(sql2)
        result_lst2 = results.fetchall()

        self.assertIs(type(result_lst[0][0]), str)
        self.assertIn(('48331',), result_lst)
        self.assertIs(type(result_lst2[0][0]), int)
        self.assertGreater(len(result_lst[0][0]), 0)
        self.assertGreater(len(str(result_lst2[0][0])), 0)


unittest.main(verbosity=2)
