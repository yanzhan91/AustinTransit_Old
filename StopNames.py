from psycopg2.pool import ThreadedConnectionPool
import logging

conn_string = "host='austintransitinstance.ctcua5myzdfi.us-east-1.rds.amazonaws.com' port='5432' " \
              "dbname='austintransitdb' user='austintransit_readonly' password='readonly'"

global pool
pool = None


def get_stop_name(stop_id):
    logging.info('Geting stop name for %s' % stop_id)
    try:
        if not pool:
            __get_pool()

        conn = pool.getconn()
        cursor = conn.cursor()
        cursor.execute('select stop_name from stops where stop_id=%s ' % stop_id)
        records = cursor.fetchall()

        pool.putconn(conn)

        if not records:
            return ''
        else:
            logging.info('stop_id %s at %s' % (stop_id, records[0][0]))
            return records[0][0].replace('&', 'and')
    except Exception as e:
        logging.info(e)
        return ''


def __get_pool():
    global pool
    pool = ThreadedConnectionPool(5, 10, conn_string)

if __name__ == "__main__":
    print(get_stop_name('1174'))
