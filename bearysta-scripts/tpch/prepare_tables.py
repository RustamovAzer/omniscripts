import sys

query_template = """
USER admin omnisci {{

CREATE TABLE NATION  ( N_NATIONKEY  INTEGER NOT NULL,
                            N_NAME       CHAR(25) NOT NULL,
                            N_REGIONKEY  INTEGER NOT NULL,
                            N_COMMENT    VARCHAR(152)) WITH (FRAGMENT_SIZE={nation_fs});

CREATE TABLE REGION  ( R_REGIONKEY  INTEGER NOT NULL,
                            R_NAME       CHAR(25) NOT NULL,
                            R_COMMENT    VARCHAR(152)) WITH (FRAGMENT_SIZE={region_fs});

CREATE TABLE PART  ( P_PARTKEY     INTEGER NOT NULL,
                          P_NAME        VARCHAR(55) NOT NULL,
                          P_MFGR        CHAR(25) NOT NULL,
                          P_BRAND       CHAR(10) NOT NULL,
                          P_TYPE        VARCHAR(25) NOT NULL,
                          P_SIZE        INTEGER NOT NULL,
                          P_CONTAINER   CHAR(10) NOT NULL,
                          P_RETAILPRICE DECIMAL(15,2) NOT NULL,
                          P_COMMENT     VARCHAR(23) NOT NULL ) WITH (FRAGMENT_SIZE={part_fs});

CREATE TABLE SUPPLIER ( S_SUPPKEY     INTEGER NOT NULL,
                             S_NAME        CHAR(25) NOT NULL,
                             S_ADDRESS     VARCHAR(40) NOT NULL,
                             S_NATIONKEY   INTEGER NOT NULL,
                             S_PHONE       CHAR(15) NOT NULL,
                             S_ACCTBAL     DECIMAL(15,2) NOT NULL,
                             S_COMMENT     VARCHAR(101) NOT NULL) WITH (FRAGMENT_SIZE={supplier_fs});

CREATE TABLE PARTSUPP ( PS_PARTKEY     INTEGER NOT NULL,
                             PS_SUPPKEY     INTEGER NOT NULL,
                             PS_AVAILQTY    INTEGER NOT NULL,
                             PS_SUPPLYCOST  DECIMAL(15,2)  NOT NULL,
                             PS_COMMENT     VARCHAR(199) NOT NULL ) WITH (FRAGMENT_SIZE={partsupp_fs});

CREATE TABLE CUSTOMER ( C_CUSTKEY     INTEGER NOT NULL,
                             C_NAME        VARCHAR(25) NOT NULL,
                             C_ADDRESS     VARCHAR(40) NOT NULL,
                             C_NATIONKEY   INTEGER NOT NULL,
                             C_PHONE       CHAR(15) NOT NULL,
                             C_ACCTBAL     DECIMAL(15,2)   NOT NULL,
                             C_MKTSEGMENT  CHAR(10) NOT NULL,
                             C_COMMENT     VARCHAR(117) NOT NULL) WITH (FRAGMENT_SIZE={customer_fs});

CREATE TABLE ORDERS  ( O_ORDERKEY       INTEGER NOT NULL,
                           O_CUSTKEY        INTEGER NOT NULL,
                           O_ORDERSTATUS    CHAR(1) NOT NULL,
                           O_TOTALPRICE     DECIMAL(15,2) NOT NULL,
                           O_ORDERDATE      DATE NOT NULL,
                           O_ORDERPRIORITY  CHAR(15) NOT NULL,
                           O_CLERK          CHAR(15) NOT NULL,
                           O_SHIPPRIORITY   INTEGER NOT NULL,
                           O_COMMENT        VARCHAR(79) NOT NULL) WITH (FRAGMENT_SIZE={orders_fs});

CREATE TABLE LINEITEM ( L_ORDERKEY    INTEGER NOT NULL,
                             L_PARTKEY     INTEGER NOT NULL,
                             L_SUPPKEY     INTEGER NOT NULL,
                             L_LINENUMBER  INTEGER NOT NULL,
                             L_QUANTITY    DECIMAL(15,2) NOT NULL,
                             L_EXTENDEDPRICE  DECIMAL(15,2) NOT NULL,
                             L_DISCOUNT    DECIMAL(15,2) NOT NULL,
                             L_TAX         DECIMAL(15,2) NOT NULL,
                             L_RETURNFLAG  CHAR(1) NOT NULL,
                             L_LINESTATUS  CHAR(1) NOT NULL,
                             L_SHIPDATE    DATE NOT NULL,
                             L_COMMITDATE  DATE NOT NULL,
                             L_RECEIPTDATE DATE NOT NULL,
                             L_SHIPINSTRUCT CHAR(25) NOT NULL,
                             L_SHIPMODE     CHAR(10) NOT NULL,
                             L_COMMENT      VARCHAR(44) NOT NULL) WITH (FRAGMENT_SIZE={lineitem_fs});

COPY customer FROM '{data_folder}/customer.tbl' WITH (header='false',delimiter='|');
COPY lineitem FROM '{data_folder}/lineitem.tbl' WITH (header='false',delimiter='|');
COPY nation FROM '{data_folder}/nation.tbl' WITH (header='false',delimiter='|');
COPY orders FROM '{data_folder}/orders.tbl' WITH (header='false',delimiter='|');
COPY partsupp FROM '{data_folder}/partsupp.tbl' WITH (header='false',delimiter='|');
COPY part FROM '{data_folder}/part.tbl' WITH (header='false',delimiter='|');
COPY region FROM '{data_folder}/region.tbl' WITH (header='false',delimiter='|');
COPY supplier FROM '{data_folder}/supplier.tbl' WITH (header='false',delimiter='|');
}}
"""

data_folder = sys.argv[1]
num_threads = sys.argv[2]
num_slack = sys.argv[3]
num_frags = int(num_threads) * int(num_slack)


def get_line_count(filename):
    line_count = 0
    with open(filename, "r") as f:
        for _ in f.readlines():
            line_count += 1
    return line_count


fragment_sizes = {
    table
    + "_fs": max(
        [get_line_count("{}/{}.tbl".format(data_folder, table)) // int(num_frags), 3000000]
    )
    for table in [
        "customer",
        "lineitem",
        "nation",
        "orders",
        "partsupp",
        "part",
        "region",
        "supplier",
    ]
}


print(fragment_sizes)
with open(data_folder + "/create_tables.sql", "w") as f:
    f.write(query_template.format(**fragment_sizes, data_folder=data_folder))
