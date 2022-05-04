DROP TABLE IF EXISTS ORDERS CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;
DROP TABLE IF EXISTS POSITION CASCADE;
DROP TABLE IF EXISTS ACCOUNT CASCADE;

CREATE TABLE ACCOUNT (
    ACCOUNT_ID SERIAL,
    Balance real NOT NULL,
    PRIMARY KEY (ACCOUNT_ID)
);

CREATE TABLE POSITION (
    POSITION_ID SERIAL,
    SYMBOL varchar(10) NOT NULL,
    AMOUNT real NOT NULL, /* positive real number */
    ACCOUNT_ID int NOT NULL,
    unique(ACCOUNT_ID, SYMBOL),
    PRIMARY KEY (POSITION_ID),
    FOREIGN KEY(ACCOUNT_ID) REFERENCES ACCOUNT(ACCOUNT_ID) ON DELETE CASCADE
);

CREATE TYPE ORDER_STATUS AS ENUM (
    'open', 'canceled','executed'
);

CREATE TABLE ORDERS (
    ORDER_ID SERIAL,
    TRANS_ID int NOT NULL,
    SYMBOL varchar(10) NOT NULL,
    AMOUNT real NOT NULL, -- +means to purchase, - means to sell
    LIMIT_PRICE real NOT NULL, 
    ACCOUNT_ID int NOT NULL,
    TIME timestamp NOT NULL, 
    status ORDER_STATUS NOT NULL DEFAULT 'open',
    PRIMARY KEY(ORDER_ID),
    FOREIGN KEY(ACCOUNT_ID) REFERENCES ACCOUNT(ACCOUNT_ID) ON DELETE CASCADE
);

