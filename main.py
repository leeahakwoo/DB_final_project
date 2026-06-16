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
.info-box {
    background-color: #f8fafc;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📦 재고관리")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "상품별 현재 재고 현황",
        "공급자별 공급 상품 조회",
        "입출고 이력 조회",
        "SQL Console"
    ]
)

st.markdown('<div class="main-title">재고관리 정보시스템</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">SQLite 데이터베이스와 Streamlit을 연동한 재고관리 조회 시스템</div>',
    unsafe_allow_html=True
)

if menu == "상품별 현재 재고 현황":
    st.subheader("상품별 현재 재고 현황")

    st.markdown(
        """
        <div class="info-box">
        Product, Inventory, Warehouse 테이블을 JOIN하여 상품별 현재 재고 수량과 창고 위치를 조회한다.
        </div>
        """,
        unsafe_allow_html=True
    )

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

    df = run_query(query)

    st.markdown("#### 조회 결과")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "공급자별 공급 상품 조회":
    st.subheader("공급자별 공급 상품 조회")

    st.markdown(
        """
        <div class="info-box">
        Supplier, SupplierProduct, Product 테이블을 JOIN하여 공급자별 공급 상품과 공급 단가를 조회한다.
        </div>
        """,
        unsafe_allow_html=True
    )

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

    df = run_query(query)

    st.markdown("#### 조회 결과")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "입출고 이력 조회":
    st.subheader("입출고 이력 조회")

    st.markdown(
        """
        <div class="info-box">
        StockTransaction, Product, Warehouse 테이블을 JOIN하여 상품별 입출고 이력과 거래 담당자를 조회한다.
        </div>
        """,
        unsafe_allow_html=True
    )

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

    df = run_query(query)

    st.markdown("#### 조회 결과")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "SQL Console":
    st.subheader("SQL Console")

    st.markdown(
        """
        <div class="info-box">
        사용자가 직접 SELECT 조회문을 입력하여 SQLite 데이터베이스의 데이터를 조회할 수 있다.
        </div>
        """,
        unsafe_allow_html=True
    )

    sample_queries = {
        "상품별 현재 재고 현황": """
SELECT
    P.product_name AS 상품명,
    W.warehouse_name AS 창고명,
    I.current_qty AS 현재재고
FROM Product P
JOIN Inventory I
    ON P.product_id = I.product_id
JOIN Warehouse W
    ON I.warehouse_id = W.warehouse_id;
""",
        "공급자별 공급 상품 조회": """
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
""",
        "입출고 이력 조회": """
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
""",
        "전체 상품 조회": """
SELECT * FROM Product;
""",
        "전체 재고 조회": """
SELECT * FROM Inventory;
"""
    }

    selected_sample = st.selectbox(
        "예제 SQL 선택",
        list(sample_queries.keys())
    )

    user_query = st.text_area(
        "SQL 입력",
        value=sample_queries[selected_sample],
        height=260
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        run_btn = st.button("조회 실행")

    with col2:
        st.caption("SELECT 조회문 실행을 기준으로 구성한 화면입니다.")

    if run_btn:
        try:
            if not user_query.strip().lower().startswith("select"):
                st.error("현재 화면에서는 SELECT 조회문만 실행할 수 있습니다.")
            else:
                df = run_query(user_query)
                st.success("조회가 완료되었습니다.")
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"SQL 실행 중 오류가 발생했습니다: {e}")
