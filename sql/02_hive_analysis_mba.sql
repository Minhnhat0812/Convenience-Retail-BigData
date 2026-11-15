set hive.exec.mode.local.auto=true;
USE retail_dw;

-- ==========================================
-- NHÓM 1: PHÂN TÍCH DOANH THU VÀ GIAO DỊCH
-- ==========================================

-- Q1: Doanh thu theo Tháng, Quý, Năm (Đã bổ sung tháng)
SELECT t.trans_year, t.trans_month, t.trans_quarter, SUM(f.Total_Cost) as revenue
FROM fact_sales f JOIN dim_time t ON f.Date_str = t.Date_str
GROUP BY t.trans_year, t.trans_month, t.trans_quarter 
ORDER BY t.trans_year, t.trans_month;

-- Q2: Phương thức thanh toán đóng góp vào số lượng giao dịch và doanh thu
SELECT Payment_Method, 
       COUNT(Transaction_ID) as total_transactions, 
       SUM(Total_Cost) as total_revenue
FROM fact_sales
GROUP BY Payment_Method 
ORDER BY total_revenue DESC;

-- Q3: Sự khác biệt về giá trị giao dịch trung bình giữa các nhóm khuyến mãi
SELECT Promotion, 
       AVG(Total_Cost) as avg_transaction_value
FROM fact_sales
GROUP BY Promotion 
ORDER BY avg_transaction_value DESC;

-- Q4: Đóng góp của các nhóm khách hàng vào số lượng giao dịch và doanh thu
SELECT c.Customer_Category, 
       COUNT(f.Transaction_ID) as total_transactions, 
       SUM(f.Total_Cost) as total_revenue
FROM fact_sales f 
JOIN dim_customer c ON f.Customer_Name = c.Customer_Name
GROUP BY c.Customer_Category 
ORDER BY total_revenue DESC;

-- ==========================================
-- NHÓM 2: PHÂN TÍCH KHÁCH HÀNG VÀ SẢN PHẨM
-- ==========================================

-- Q5: Thành viên vs Không thành viên (Giá trị TB và Số lượng SP TB)
SELECT c.Member, 
       AVG(f.Total_Cost) as avg_transaction_value, 
       AVG(f.Total_Items) as avg_items
FROM fact_sales f 
JOIN dim_customer c ON f.Customer_Name = c.Customer_Name
GROUP BY c.Member;

-- Q6: Top 10 sản phẩm mua nhiều nhất
SELECT product_name, 
       COUNT(Transaction_ID) as purchase_frequency
FROM fact_transaction_items
GROUP BY product_name 
ORDER BY purchase_frequency DESC 
LIMIT 10;

-- Q7: Doanh thu, số lượng giao dịch và quy mô giỏ hàng theo Mùa
SELECT t.Season, 
       COUNT(f.Transaction_ID) as total_transactions, 
       SUM(f.Total_Cost) as total_revenue,
       AVG(f.Total_Items) as avg_basket_size
FROM fact_sales f 
JOIN dim_time t ON f.Date_str = t.Date_str
GROUP BY t.Season 
ORDER BY total_revenue DESC;

-- ==========================================
-- NHÓM 3: PHÂN TÍCH GIỎ HÀNG (MBA)
-- ==========================================

-- Q8 & Q9: Tìm cặp sản phẩm mua cùng nhau và tính Support (%)
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
    b.item1, 
    b.item2, 
    COUNT(b.Transaction_ID) as frequency,
    (CAST(COUNT(b.Transaction_ID) AS DOUBLE) / MAX(tt.total_tx)) * 100 AS support_percentage
FROM Basket b 
CROSS JOIN Total_Transactions tt
GROUP BY b.item1, b.item2
ORDER BY frequency DESC
LIMIT 20;