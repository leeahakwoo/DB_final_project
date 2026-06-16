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
.metric-card {
    padding: 20px;
    border-radius: 14px;
    background-color: #f7f9fc;
    border: 1px solid #e5e7eb;
}
.status-low {
    color: #dc2626;
    font-weight: 700;
}
.status-normal {
    color: #15803d;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📦 재고관리")
menu = st.sidebar.radio(
    "메뉴",
    [
        "대시보드",
        "상품별 재고 현황",
        "발주 필요 품목",
        "입출고 이력",
        "공급자별 공급 상품"
    ]
)

st.markdown('<div class="main-title">재고관리 정보시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">상품, 창고, 입출고 및 재고거래 이력을 통합 관리하는 SQLite 기반 정보시스템</div>', unsafe_allow_html=True)

# 공통 데이터
product_count = run_query("SELECT COUNT(*) AS cnt FROM Product;")["cnt"][0]
warehouse_count = run_query("SELECT COUNT(*) AS cnt FROM Warehouse;")["cnt"][0]
total_stock = run_query("SELECT SUM(current_qty) AS total FROM Inventory;")["total"][0]
transaction_count = run_query("SELECT COUNT(*) AS cnt FROM StockTransaction;")["cnt"][0]

if menu == "대시보드":
    st.subheader("📊 재고관리 대시보드")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("등록 상품 수", f"{product_count}개")
    col2.metric("운영 창고 수", f"{warehouse_count}개")
    col3.metric("전체 재고 수량", f"{total_stock}개")
    col4.metric("입출고 거래 건수", f"{transaction_count}건")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("창고별 재고 총량")
        query = """
        SELECT 
            W.warehouse_name AS 창고명,
            SUM(I.current_qty) AS 재고수량
        FROM Inventory I
        JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
        GROUP BY W.warehouse_name
        ORDER BY 재고수량 DESC;
        """
        df = run_query(query)
        st.bar_chart(df.set_index("창고명"))

    with col_right:
        st.subheader("상품 분류별 평균 가격")
        query = """
        SELECT 
            category AS 상품분류,
            AVG(base_price) AS 평균가격
        FROM Product
        GROUP BY category;
        """
        df = run_query(query)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "상품별 재고 현황":
    st.subheader("📋 상품별 재고 현황")

    query = """
    SELECT 
        P.product_name AS 상품명,
        P.category AS 분류,
        W.warehouse_name AS 창고명,
        I.current_qty AS 현재재고,
        I.safety_qty AS 안전재고,
        I.max_qty AS 최대재고,
        CASE
            WHEN I.current_qty <= I.safety_qty THEN '발주 필요'
            ELSE '정상'
        END AS 재고상태
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    ORDER BY I.current_qty ASC;
    """

    df = run_query(query)

    selected_category = st.selectbox(
        "상품 분류 선택",
        ["전체"] + sorted(df["분류"].unique().tolist())
    )

    if selected_category != "전체":
        df = df[df["분류"] == selected_category]

    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "발주 필요 품목":
    st.subheader("🚨 발주 필요 품목")

    query = """
    SELECT 
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        I.current_qty AS 현재재고,
        I.safety_qty AS 안전재고,
        I.max_qty AS 최대재고,
        I.max_qty - I.current_qty AS 발주필요수량
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    WHERE I.current_qty <= I.safety_qty
    ORDER BY 발주필요수량 DESC;
    """

    df = run_query(query)

    if len(df) == 0:
        st.success("현재 안전재고 이하 품목이 없습니다.")
    else:
        st.warning(f"발주가 필요한 품목이 {len(df)}건 있습니다.")
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "입출고 이력":
    st.subheader("🔄 입출고 이력")

    query = """
    SELECT 
        ST.transaction_date AS 거래일자,
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        ST.transaction_type AS 거래유형,
        ST.quantity AS 수량,
        ST.reason AS 사유,
        ST.manager AS 담당자
    FROM StockTransaction ST
    JOIN Product P ON ST.product_id = P.product_id
    JOIN Warehouse W ON ST.warehouse_id = W.warehouse_id
    ORDER BY ST.transaction_date DESC;
    """

    df = run_query(query)

    transaction_type = st.selectbox(
        "거래유형 선택",
        ["전체", "입고", "출고"]
    )

    if transaction_type != "전체":
        df = df[df["거래유형"] == transaction_type]

    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "공급자별 공급 상품":
    st.subheader("🏭 공급자별 공급 상품")

    query = """
    SELECT 
        S.supplier_name AS 공급자명,
        S.phone AS 연락처,
        P.product_name AS 상품명,
        P.category AS 분류,
        SP.supply_price AS 공급단가,
        SP.min_order_qty AS 최소주문수량,
        SP.lead_day AS 납기일
    FROM SupplierProduct SP
    JOIN Supplier S ON SP.supplier_id = S.supplier_id
    JOIN Product P ON SP.product_id = P.product_id
    ORDER BY S.supplier_name;
    """

    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)
