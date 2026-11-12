USE retail_dw;

-- Q1: Doanh thu bán hàng biến động theo Quý và Năm
SELECT t.trans_year, t.trans_quarter, SUM(f.Total_Cost) as revenue
FROM fact_sales f JOIN dim_time t ON f.Date_str = t.Date_str
GROUP BY t.trans_year, t.trans_quarter ORDER BY t.trans_year, t.trans_quarter;

-- Q5: Giá trị giao dịch trung bình giữa Thành viên và Không thành viên
SELECT c.Member, AVG(f.Total_Cost) as avg_transaction_value, AVG(f.Total_Items) as avg_items
FROM fact_sales f JOIN dim_customer c ON f.Customer_Name = c.Customer_Name
GROUP BY c.Member;

-- Q6: Top 10 sản phẩm mua nhiều nhất
SELECT product_name, COUNT(Transaction_ID) as purchase_frequency
FROM fact_transaction_items
GROUP BY product_name ORDER BY purchase_frequency DESC LIMIT 10;

-- Q8 & Q9: Market Basket Analysis (Tìm cặp sản phẩm mua cùng nhau và tính Support)
WITH Basket AS (
    SELECT t1.Transaction_ID, t1.product_name AS item1, t2.product_name AS item2
    FROM fact_transaction_items t1
    JOIN fact_transaction_items t2 ON t1.Transaction_ID = t2.Transaction_ID
    WHERE t1.product_name < t2.product_name
),
Total_Transactions AS (
    SELECT COUNT(DISTINCT Transaction_ID) as total_tx FROM fact_sales
)
SELECT 
    b.item1, b.item2, COUNT(b.Transaction_ID) as frequency,
    (COUNT(b.Transaction_ID) / MAX(tt.total_tx)) * 100 AS support_percentage
FROM Basket b CROSS JOIN Total_Transactions tt
GROUP BY b.item1, b.item2
ORDER BY frequency DESC
LIMIT 20;