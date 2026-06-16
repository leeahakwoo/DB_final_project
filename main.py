import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "inventory.db"

st.set_page_config(
    page_title="재고관리 정보시스템",
    page_icon="📦",
    layout="wide"
)

def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}
.sub-text {
    color: #666;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📦 재고관리")
menu = st.sidebar.radio(
    "조회 메뉴",
    [
        "상품별 현재 재고 현황",
        "공급자별 공급 상품 조회",
        "입출고 이력 조회"
    ]
)

st.markdown('<div class="main-title">재고관리 정보시스템</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">SQLite 데이터베이스와 Streamlit을 연동한 재고관리 조회 화면</div>',
    unsafe_allow_html=True
)

if menu == "상품별 현재 재고 현황":
    st.subheader("상품별 현재 재고 현황")

    query = """
SELECT
    P.product_name AS 상품명,
    W.warehouse_name AS 창고명,
    I.current_qty AS 현재재고
FROM Product P
JOIN Inventory I
    ON P.product_id = I.product_id
JOIN Warehouse W
    ON I.warehouse_id = W.warehouse_id;
"""

    st.markdown("#### 실행 SQL")
    st.code(query, language="sql")

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "공급자별 공급 상품 조회":
    st.subheader("공급자별 공급 상품 조회")

    query = """
SELECT
    S.supplier_name AS 공급자명,
    P.product_name AS 상품명,
    SP.supply_price AS 공급단가,
    SP.lead_day AS 납기일
FROM Supplier S
JOIN SupplierProduct SP
    ON S.supplier_id = SP.supplier_id
JOIN Product P
    ON SP.product_id = P.product_id;
"""

    st.markdown("#### 실행 SQL")
    st.code(query, language="sql")

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "입출고 이력 조회":
    st.subheader("입출고 이력 조회")

    query = """
SELECT
    P.product_name AS 상품명,
    W.warehouse_name AS 창고명,
    ST.transaction_type AS 거래유형,
    ST.quantity AS 수량,
    ST.transaction_date AS 거래일자,
    ST.manager AS 담당자
FROM StockTransaction ST
JOIN Product P
    ON ST.product_id = P.product_id
JOIN Warehouse W
    ON ST.warehouse_id = W.warehouse_id
ORDER BY ST.transaction_date DESC;
"""

    st.markdown("#### 실행 SQL")
    st.code(query, language="sql")

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)
