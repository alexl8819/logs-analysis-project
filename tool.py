#!/usr/bin/env python
""" Log viewer tool """

from __future__ import print_function
from os.path import isfile
from argparse import ArgumentParser
from psycopg2 import connect, Error

LOG_HEADER = '========================= Log Report ========================='

Q_ONE = '1. What are the most popular three articles of all time?'
Q_ONE_VIEW = """ CREATE VIEW question_one as SELECT title,
     count(*)::integer AS views FROM articles LEFT JOIN log
     ON substring(log.path FROM '[a-zA-Z0-9-]+$') = articles.slug
     GROUP BY articles.title ORDER BY views desc LIMIT 3; """
Q_ONE_QUERY = 'SELECT * FROM question_one;'

Q_TWO = '2. Who are the most popular article authors of all time?'
Q_TWO_VIEW = """ CREATE VIEW question_two as SELECT DISTINCT authors.name,
     count(*)::integer AS views FROM articles LEFT JOIN log ON
     substring(log.path FROM '[a-zA-Z0-9-]+$') = articles.slug INNER JOIN
     authors ON articles.author = authors.id GROUP BY authors.name
     ORDER BY views desc; """
Q_TWO_QUERY = 'SELECT * FROM question_two;'

Q_THREE = '3. On which days did more than 1% of requests lead to errors?'
Q_THREE_VIEW = """ CREATE VIEW question_three as SELECT * FROM
     (SELECT DISTINCT date(time) AS datetime, round(100.0 * ((count(*)
     FILTER (WHERE substring(status, '\\d{3}')::numeric >= 400))::float /
     count(*)::float)::numeric, 2)::float AS percent FROM log
     GROUP BY datetime ORDER BY datetime asc) ss
     WHERE percent > 1.0; """
Q_THREE_QUERY = 'SELECT * FROM question_three;'


def append_to_log(filename, *args):
    """ Appends entry to logfile """
    file_exists = isfile(filename)
    with open(filename, 'a+') as log:
        log.write(('{}\n' if not file_exists
                   else '\n{}\n').format('\n'.join(args)))


def query(conn, statement, results=True):
    """ Runs a query on a given cursor """
    records = []

    with conn.cursor() as cursor:
        try:
            cursor.execute(statement)
            if results:
                records = cursor.fetchall()
        except Error:
            conn.rollback()
        else:
            conn.commit()

    return records


def create_views(dbname):
    """ Creates views for a given database """
    with connect('dbname={}'.format(dbname)) as conn:
        if not query(conn, Q_ONE_QUERY):
            query(conn, Q_ONE_VIEW, False)
            print('View (question_one) created')
        else:
            print('View (question_one) already exists')

        if not query(conn, Q_TWO_QUERY):
            query(conn, Q_TWO_VIEW, False)
            print('View (question_two) created')
        else:
            print('View (question_two) already exists')

        if not query(conn, Q_THREE_QUERY):
            query(conn, Q_THREE_VIEW, False)
            print('View (question_three) created')
        else:
            print('View (question_three) already exists')


def create_report(dbname, logfile='report.log'):
    """ Creates a new report """
    with connect('dbname={}'.format(dbname)) as conn:
        # Append questions and answers from instructions if available
        append_to_log(logfile, LOG_HEADER)

        answer_one = ['"{}" - {} views'.format(r[0], r[1])
                      for r in query(conn, Q_ONE_QUERY)]

        if answer_one:
            append_to_log(logfile, Q_ONE, '', '\n'.join(answer_one))

        answer_two = ['"{}" - {} views'.format(r[0], r[1])
                      for r in query(conn, Q_TWO_QUERY)]

        if answer_two:
            append_to_log(logfile, Q_TWO, '', '\n'.join(answer_two))

        answer_three = ['"{}" - {}% errors'.format(r[0], r[1])
                        for r in query(conn, Q_THREE_QUERY)]

        if answer_three:
            append_to_log(logfile, Q_THREE, '', '\n'.join(answer_three))

    print('Report generated: {}'.format(logfile))


def main():
    """ Main function """
    parser = ArgumentParser(prog='Reporting Tool')
    parser.add_argument('action', default='create_report',
                        help="create views or report")
    parser.add_argument('--logfile', default='report.log',
                        help='logfile to write report to')
    parser.add_argument('--dbname', default='news',
                        help='name of database to query from')
    args = parser.parse_args()
    # use parsed args to determine action
    if args.action == 'create_report':
        create_report(args.dbname, args.logfile)
    elif args.action == 'create_views':
        create_views(args.dbname)
    else:
        exit('Invalid action: {}'.format(args.action))

if __name__ == '__main__':
    main()
