import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "inventory.db"

st.set_page_config(
    page_title="재고관리 정보시스템",
    page_icon="📦",
    layout="wide"
)

# =========================
# DB 공통 함수
# =========================
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_query(query, params=None):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params or ())
    conn.close()
    return df

def execute_sql(query, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    conn.close()

# =========================
# 스타일
# =========================
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

# =========================
# 사이드바
# =========================
st.sidebar.title("📦 재고관리")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "대시보드",
        "상품 관리",
        "재고 현황",
        "입고 처리",
        "출고 처리",
        "거래 이력",
        "공급자 관리",
        "활용 사례 1. 상품별 현재 재고 현황",
        "활용 사례 2. 공급자별 공급 상품 조회",
        "활용 사례 3. 입출고 이력 조회",
        "SQL Console"
    ]
)

st.markdown('<div class="main-title">재고관리 정보시스템</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">SQLite 데이터베이스와 Streamlit을 연동한 재고관리 정보시스템</div>',
    unsafe_allow_html=True
)

# =========================
# 대시보드
# =========================
if menu == "대시보드":
    st.subheader("📊 대시보드")

    product_count = run_query("SELECT COUNT(*) AS cnt FROM Product;")["cnt"][0]
    supplier_count = run_query("SELECT COUNT(*) AS cnt FROM Supplier;")["cnt"][0]
    warehouse_count = run_query("SELECT COUNT(*) AS cnt FROM Warehouse;")["cnt"][0]
    total_stock = run_query("SELECT COALESCE(SUM(current_qty), 0) AS total FROM Inventory;")["total"][0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("등록 상품 수", f"{product_count}개")
    col2.metric("공급자 수", f"{supplier_count}개")
    col3.metric("운영 창고 수", f"{warehouse_count}개")
    col4.metric("전체 재고 수량", f"{total_stock}개")

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
            ROUND(AVG(base_price), 0) AS 평균가격
        FROM Product
        GROUP BY category;
        """
        df = run_query(query)
        st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# 상품 관리
# =========================
elif menu == "상품 관리":
    st.subheader("📦 상품 관리")

    tab1, tab2, tab3 = st.tabs(["상품 목록", "상품 등록", "상품 수정/삭제"])

    with tab1:
        query = """
        SELECT 
            product_id AS 상품ID,
            product_name AS 상품명,
            spec AS 규격,
            unit AS 단위,
            base_price AS 기준가격,
            category AS 분류,
            status AS 상태
        FROM Product
        ORDER BY product_id;
        """
        df = run_query(query)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 신규 상품 등록")

        with st.form("product_insert_form"):
            product_name = st.text_input("상품명")
            spec = st.text_input("규격")
            unit = st.selectbox("단위", ["EA", "BOX", "SET"])
            base_price = st.number_input("기준가격", min_value=0, step=1000)
            category = st.selectbox("분류", ["전자제품", "사무용품", "가구", "기타"])
            status = st.selectbox("상태", ["정상", "중지"])

            submitted = st.form_submit_button("상품 등록")

            if submitted:
                if product_name.strip() == "":
                    st.error("상품명을 입력하세요.")
                else:
                    execute_sql(
                        """
                        INSERT INTO Product
                        (product_name, spec, unit, base_price, category, status)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (product_name, spec, unit, base_price, category, status)
                    )
                    st.success("상품이 등록되었습니다.")
                    st.rerun()

    with tab3:
        st.markdown("### 상품 수정/삭제")

        products = run_query("SELECT product_id, product_name FROM Product ORDER BY product_id;")

        product_map = {
            f"{row.product_id} - {row.product_name}": row.product_id
            for row in products.itertuples()
        }

        selected = st.selectbox("수정/삭제할 상품 선택", list(product_map.keys()))

        if selected:
            product_id = product_map[selected]
            item = run_query("SELECT * FROM Product WHERE product_id = ?;", (product_id,))

            if not item.empty:
                row = item.iloc[0]

                with st.form("product_update_form"):
                    product_name = st.text_input("상품명", row["product_name"])
                    spec = st.text_input("규격", row["spec"] if row["spec"] else "")
                    unit = st.text_input("단위", row["unit"] if row["unit"] else "EA")
                    base_price = st.number_input("기준가격", min_value=0, value=int(row["base_price"]))
                    category = st.text_input("분류", row["category"] if row["category"] else "")
                    status_options = ["정상", "중지", "삭제"]
                    status_index = status_options.index(row["status"]) if row["status"] in status_options else 0
                    status = st.selectbox("상태", status_options, index=status_index)

                    col1, col2 = st.columns(2)
                    update_btn = col1.form_submit_button("수정 저장")
                    delete_btn = col2.form_submit_button("삭제 처리")

                    if update_btn:
                        execute_sql(
                            """
                            UPDATE Product
                            SET product_name = ?, spec = ?, unit = ?, base_price = ?, category = ?, status = ?
                            WHERE product_id = ?;
                            """,
                            (product_name, spec, unit, base_price, category, status, product_id)
                        )
                        st.success("상품 정보가 수정되었습니다.")
                        st.rerun()

                    if delete_btn:
                        execute_sql(
                            """
                            UPDATE Product
                            SET status = '삭제'
                            WHERE product_id = ?;
                            """,
                            (product_id,)
                        )
                        st.warning("상품이 삭제 상태로 변경되었습니다.")
                        st.rerun()

# =========================
# 재고 현황 및 재고 수정
# =========================
elif menu == "재고 현황":
    st.subheader("📋 재고 현황")

    query = """
    SELECT 
        I.inventory_id AS 재고ID,
        P.product_name AS 상품명,
        P.category AS 분류,
        W.warehouse_name AS 창고명,
        I.current_qty AS 현재재고,
        I.safety_qty AS 안전재고,
        I.max_qty AS 최대재고,
        CASE
            WHEN I.current_qty <= I.safety_qty THEN '발주 필요'
            ELSE '정상'
        END AS 재고상태,
        I.update_date AS 최종수정일
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    ORDER BY I.current_qty ASC;
    """

    df = run_query(query)

    col1, col2 = st.columns(2)
    selected_status = col1.selectbox("재고상태", ["전체", "정상", "발주 필요"])
    selected_category = col2.selectbox("상품분류", ["전체"] + sorted(df["분류"].dropna().unique().tolist()))

    if selected_status != "전체":
        df = df[df["재고상태"] == selected_status]

    if selected_category != "전체":
        df = df[df["분류"] == selected_category]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 재고 수량 직접 수정")

    inventory_list = run_query("""
    SELECT 
        I.inventory_id,
        P.product_name,
        W.warehouse_name,
        I.current_qty,
        I.safety_qty,
        I.max_qty
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    ORDER BY I.inventory_id;
    """)

    inventory_map = {
        f"{row.inventory_id} - {row.product_name} / {row.warehouse_name}": row.inventory_id
        for row in inventory_list.itertuples()
    }

    selected_inv = st.selectbox("수정할 재고 선택", list(inventory_map.keys()))

    if selected_inv:
        inv_id = inventory_map[selected_inv]
        inv_row = inventory_list[inventory_list["inventory_id"] == inv_id].iloc[0]

        with st.form("inventory_update_form"):
            current_qty = st.number_input("현재재고", min_value=0, value=int(inv_row["current_qty"]))
            safety_qty = st.number_input("안전재고", min_value=0, value=int(inv_row["safety_qty"]))
            max_qty = st.number_input("최대재고", min_value=0, value=int(inv_row["max_qty"]))

            submitted = st.form_submit_button("재고 수정")

            if submitted:
                execute_sql(
                    """
                    UPDATE Inventory
                    SET current_qty = ?, safety_qty = ?, max_qty = ?, update_date = ?
                    WHERE inventory_id = ?;
                    """,
                    (current_qty, safety_qty, max_qty, str(date.today()), inv_id)
                )
                st.success("재고 정보가 수정되었습니다.")
                st.rerun()

# =========================
# 입고 처리
# =========================
elif menu == "입고 처리":
    st.subheader("⬆ 입고 처리")

    products = run_query("SELECT product_id, product_name FROM Product WHERE status = '정상' ORDER BY product_id;")
    suppliers = run_query("SELECT supplier_id, supplier_name FROM Supplier ORDER BY supplier_id;")
    warehouses = run_query("SELECT warehouse_id, warehouse_name FROM Warehouse ORDER BY warehouse_id;")

    product_map = {f"{r.product_id} - {r.product_name}": r.product_id for r in products.itertuples()}
    supplier_map = {f"{r.supplier_id} - {r.supplier_name}": r.supplier_id for r in suppliers.itertuples()}
    warehouse_map = {f"{r.warehouse_id} - {r.warehouse_name}": r.warehouse_id for r in warehouses.itertuples()}

    with st.form("inbound_form"):
        selected_product = st.selectbox("상품 선택", list(product_map.keys()))
        selected_supplier = st.selectbox("공급자 선택", list(supplier_map.keys()))
        selected_warehouse = st.selectbox("입고 창고 선택", list(warehouse_map.keys()))
        inbound_qty = st.number_input("입고 수량", min_value=1, step=1)
        inbound_date = st.date_input("입고일자", date.today())
        inspection_yn = st.selectbox("검사여부", ["Y", "N"])
        manager = st.text_input("담당자", "관리자")

        submitted = st.form_submit_button("입고 처리")

        if submitted:
            product_id = product_map[selected_product]
            supplier_id = supplier_map[selected_supplier]
            warehouse_id = warehouse_map[selected_warehouse]

            conn = get_conn()
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO Inbound
                (supplier_id, product_id, warehouse_id, inbound_qty, inbound_date, inspection_yn, manager)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (supplier_id, product_id, warehouse_id, inbound_qty, str(inbound_date), inspection_yn, manager)
            )
            inbound_id = cur.lastrowid

            cur.execute(
                """
                UPDATE Inventory
                SET current_qty = current_qty + ?, update_date = ?
                WHERE product_id = ? AND warehouse_id = ?;
                """,
                (inbound_qty, str(inbound_date), product_id, warehouse_id)
            )

            if cur.rowcount == 0:
                cur.execute(
                    """
                    INSERT INTO Inventory
                    (product_id, warehouse_id, current_qty, safety_qty, max_qty, update_date)
                    VALUES (?, ?, ?, 0, 0, ?);
                    """,
                    (product_id, warehouse_id, inbound_qty, str(inbound_date))
                )

            cur.execute(
                """
                INSERT INTO StockTransaction
                (product_id, warehouse_id, transaction_type, quantity, transaction_date, reference_type, reference_id, reason, manager)
                VALUES (?, ?, '입고', ?, ?, 'Inbound', ?, '입고 처리', ?);
                """,
                (product_id, warehouse_id, inbound_qty, str(inbound_date), inbound_id, manager)
            )

            conn.commit()
            conn.close()

            st.success("입고 처리가 완료되었습니다.")
            st.rerun()

# =========================
# 출고 처리
# =========================
elif menu == "출고 처리":
    st.subheader("⬇ 출고 처리")

    inventory = run_query("""
    SELECT 
        I.inventory_id,
        I.product_id,
        I.warehouse_id,
        P.product_name,
        W.warehouse_name,
        I.current_qty
    FROM Inventory I
    JOIN Product P ON I.product_id = P.product_id
    JOIN Warehouse W ON I.warehouse_id = W.warehouse_id
    ORDER BY I.inventory_id;
    """)

    inv_map = {
        f"{r.inventory_id} - {r.product_name} / {r.warehouse_name} / 현재재고 {r.current_qty}": r.inventory_id
        for r in inventory.itertuples()
    }

    with st.form("outbound_form"):
        selected_inv = st.selectbox("출고 상품/창고 선택", list(inv_map.keys()))
        outbound_qty = st.number_input("출고 수량", min_value=1, step=1)
        outbound_date = st.date_input("출고일자", date.today())
        destination = st.text_input("출고처", "사용부서")
        manager = st.text_input("담당자", "관리자")

        submitted = st.form_submit_button("출고 처리")

        if submitted:
            inventory_id = inv_map[selected_inv]
            row = inventory[inventory["inventory_id"] == inventory_id].iloc[0]

            product_id = int(row["product_id"])
            warehouse_id = int(row["warehouse_id"])
            current_qty = int(row["current_qty"])

            if outbound_qty > current_qty:
                st.error("현재 재고보다 출고 수량이 많습니다.")
            else:
                conn = get_conn()
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO Outbound
                    (product_id, warehouse_id, outbound_qty, outbound_date, destination, manager)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (product_id, warehouse_id, outbound_qty, str(outbound_date), destination, manager)
                )
                outbound_id = cur.lastrowid

                cur.execute(
                    """
                    UPDATE Inventory
                    SET current_qty = current_qty - ?, update_date = ?
                    WHERE inventory_id = ?;
                    """,
                    (outbound_qty, str(outbound_date), inventory_id)
                )

                cur.execute(
                    """
                    INSERT INTO StockTransaction
                    (product_id, warehouse_id, transaction_type, quantity, transaction_date, reference_type, reference_id, reason, manager)
                    VALUES (?, ?, '출고', ?, ?, 'Outbound', ?, ?, ?);
                    """,
                    (product_id, warehouse_id, outbound_qty, str(outbound_date), outbound_id, destination, manager)
                )

                conn.commit()
                conn.close()

                st.success("출고 처리가 완료되었습니다.")
                st.rerun()

# =========================
# 거래 이력
# =========================
elif menu == "거래 이력":
    st.subheader("🔄 거래 이력")

    query = """
    SELECT 
        ST.transaction_id AS 거래ID,
        ST.transaction_date AS 거래일자,
        P.product_name AS 상품명,
        W.warehouse_name AS 창고명,
        ST.transaction_type AS 거래유형,
        ST.quantity AS 수량,
        ST.reference_type AS 참조유형,
        ST.reference_id AS 참조ID,
        ST.reason AS 사유,
        ST.manager AS 담당자
    FROM StockTransaction ST
    JOIN Product P ON ST.product_id = P.product_id
    JOIN Warehouse W ON ST.warehouse_id = W.warehouse_id
    ORDER BY ST.transaction_date DESC, ST.transaction_id DESC;
    """

    df = run_query(query)

    selected_type = st.selectbox("거래유형", ["전체", "입고", "출고"])

    if selected_type != "전체":
        df = df[df["거래유형"] == selected_type]

    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# 공급자 관리
# =========================
elif menu == "공급자 관리":
    st.subheader("🏭 공급자 관리")

    tab1, tab2 = st.tabs(["공급자별 공급 상품", "공급자 등록"])

    with tab1:
        query = """
        SELECT 
            S.supplier_name AS 공급자명,
            S.phone AS 연락처,
            S.address AS 주소,
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

    with tab2:
        st.markdown("### 신규 공급자 등록")

        with st.form("supplier_insert_form"):
            supplier_name = st.text_input("공급자명")
            phone = st.text_input("연락처")
            address = st.text_input("주소")
            avg_lead_day = st.number_input("평균납기일", min_value=0, step=1)

            submitted = st.form_submit_button("공급자 등록")

            if submitted:
                if supplier_name.strip() == "":
                    st.error("공급자명을 입력하세요.")
                else:
                    execute_sql(
                        """
                        INSERT INTO Supplier
                        (supplier_name, phone, address, avg_lead_day)
                        VALUES (?, ?, ?, ?);
                        """,
                        (supplier_name, phone, address, avg_lead_day)
                    )
                    st.success("공급자가 등록되었습니다.")
                    st.rerun()

# =========================
# 활용 사례 1
# =========================
elif menu == "활용 사례 1. 상품별 현재 재고 현황":
    st.subheader("활용 사례 1. 상품별 현재 재고 현황")

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

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# 활용 사례 2
# =========================
elif menu == "활용 사례 2. 공급자별 공급 상품 조회":
    st.subheader("활용 사례 2. 공급자별 공급 상품 조회")

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

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# 활용 사례 3
# =========================
elif menu == "활용 사례 3. 입출고 이력 조회":
    st.subheader("활용 사례 3. 입출고 이력 조회")

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

    st.markdown("#### 조회 결과")
    df = run_query(query)
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# SQL Console
# =========================
elif menu == "SQL Console":
    st.subheader("💻 SQL Console")

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

    selected_sample = st.selectbox("예제 SQL 선택", list(sample_queries.keys()))

    user_query = st.text_area(
        "SQL 입력",
        value=sample_queries[selected_sample],
        height=260
    )

    run_btn = st.button("조회 실행")

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
