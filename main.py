import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "inventory.db"

def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("재고관리 정보시스템")

menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["상품별 재고 현황", "발주 필요 품목", "입출고 이력"]
)

if menu == "상품별 재고 현황":
    st.subheader("상품별 재고 현황")

    query = """
    SELECT 
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        I.current_qty AS 현재재고,
        I.safety_qty AS 안전재고,
        I.max_qty AS 최대재고
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id;
    """

    df = run_query(query)
    st.dataframe(df)

elif menu == "발주 필요 품목":
    st.subheader("발주 필요 품목")

    query = """
    SELECT 
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        I.current_qty AS 현재재고,
        I.safety_qty AS 안전재고,
        I.max_qty - I.current_qty AS 발주필요수량
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    WHERE I.current_qty <= I.safety_qty;
    """

    df = run_query(query)
    st.dataframe(df)

elif menu == "입출고 이력":
    st.subheader("입출고 이력")

    query = """
    SELECT 
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        ST.transaction_type AS 거래유형,
        ST.quantity AS 수량,
        ST.transaction_date AS 거래일자,
        ST.reason AS 사유,
        ST.manager AS 담당자
    FROM StockTransaction ST
    JOIN Product P ON ST.product_id = P.product_id
    JOIN Warehouse W ON ST.warehouse_id = W.warehouse_id
    ORDER BY ST.transaction_date DESC;
    """

    df = run_query(query)
    st.dataframe(df)
