# Mini-Project
For Datawarehouse
### สมาชิก
1.นางสาวกนกวรรณ ทองเทพ รหัสนักศึกษา 673020243-5
   
2.นายณัฐวุฒิ กำจัดภัย รหัสนักศึกษา 673020251-6
   
3.นางสาวณิรดา อนุนิวัฒน์ รหัสนักศึกษา 673020252-4
   
4.นายภูธิป ต้นโลห์ รหัสนักศึกษา 673020261-3

5.นางสาวสุพิชชา คำสิงห์ รหัสนักศึกษา 673020265-5

6.นายสุวิชชา ผาสุข รหัสนักศึกษา 673020267-1

7.นายอพิชัย อิ่มวงค์ รหัสนักศึกษา 673020269-7

## การออกแบบและพัฒนาคลังข้อมูลเพื่อวิเคราะห์ข้อมูลการขายในธุรกิจค้าปลีก (Retail Analytics: From OLTP to OLAP Data Warehouse)

   มีวัตถุประสงค์เพื่อออกแบบและพัฒนาระบบคลังข้อมูลสำหรับธุรกิจค้าปลีก โดยนำข้อมูลจากฐานข้อมูลปฏิบัติการ (OLTP) มาผ่านกระบวนการ ETL/ELT เพื่อทำความสะอาดและแปลงข้อมูล จากนั้นจัดเก็บข้อมูลใน Data Warehouse ที่ออกแบบด้วยแนวคิด Dimensional Modeling และ Star Schema ประกอบด้วย Fact Table และ Dimension Tables เพื่อรองรับการวิเคราะห์ข้อมูลในมิติต่าง ๆ เช่น เวลา สินค้า ลูกค้า และสาขา ระบบจะนำข้อมูลจาก Data Warehouse มาวิเคราะห์ด้วยแนวคิด OLAP และพัฒนา Interactive Dashboard เพื่อแสดงยอดขาย จำนวนคำสั่งซื้อ กำไร สินค้าขายดี และตัวชี้วัดทางธุรกิจอื่น ๆ สำหรับสนับสนุนการตัดสินใจทางธุรกิจ

### Dataset & Operational Database
ความหมายของ Dataset

1. Dataset คือชุดข้อมูลที่นำมาใช้ในการทำโครงงาน โดย Dataset นี้เป็นข้อมูลเกี่ยวกับ การขายสินค้าและการดำเนินงานของร้านค้าปลีก (Retail) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า คำสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า

2. Dataset นี้เป็นข้อมูลของ ระบบการขายสินค้าของธุรกิจค้าปลีก โดยจำลองกระบวนการตั้งแต่ลูกค้าเข้ามาสั่งซื้อสินค้า จนถึงการชำระเงิน การจัดส่ง และการคืนสินค้า
ตารางหลักของ Dataset
## รายละเอียดตารางข้อมูล

| ลำดับ | ตาราง | จำนวน Records | จำนวน Columns | รายละเอียด |
|:---:|---|---:|---:|---|
| 1 | `employees` | 1,000 | 3 | ข้อมูลพนักงาน |
| 2 | `returns` | 30,000 | 3 | ข้อมูลการคืนสินค้า |
| 3 | `products` | 10,000 | 4 | ข้อมูลสินค้า |
| 4 | `suppliers` | 200 | 2 | ข้อมูลผู้จัดจำหน่าย |
| 5 | `categories` | 30 | 2 | ข้อมูลประเภทสินค้า |
| 6 | `promotions` | 50 | 2 | ข้อมูลโปรโมชั่น |
| 7 | `stores` | 100 | 2 | ข้อมูลสาขา |
| 8 | `customers` | 50,000 | 3 | ข้อมูลลูกค้า |
| 9 | `payments` | 300,000 | 3 | ข้อมูลการชำระเงิน |
| 10 | `orders` | 300,000 | 5 | ข้อมูลคำสั่งซื้อ |
| 11 | `order_items` | 600,000 | 5 | รายละเอียดสินค้าในคำสั่งซื้อ |
| 12 | `shipments` | 300,000 | 3 | ข้อมูลการจัดส่ง |
Dataset หลักทั้ง 12 ตารางมีข้อมูลรวมทั้งหมด 1,631,380 Records และ 39 Columns

https://colab.research.google.com/drive/1cb03m3na2yEKvnH9-JK1oxXGFHjB0PGo#scrollTo=b8417809

3. OLTP (Online Transaction Processing)

OLTP (Online Transaction Processing) หรือ ระบบประมวลผลรายการธุรกรรมออนไลน์ เป็นระบบฐานข้อมูลที่ใช้สำหรับจัดเก็บและประมวลผลธุรกรรมที่เกิดขึ้นจากการดำเนินงานประจำวันขององค์กร โดยมีจุดมุ่งหมายเพื่อให้สามารถบันทึก แก้ไข และเรียกใช้ข้อมูลธุรกรรมได้อย่างรวดเร็ว ถูกต้อง และเป็นระบบ รวมถึงสามารถรองรับธุรกรรมจำนวนมากและการทำงานของผู้ใช้งานหลายคนพร้อมกัน

สำหรับ Dataset ที่นำมาใช้ในโครงงานนี้ มีลักษณะเป็นข้อมูลของ ระบบธุรกิจค้าปลีก (Retail Business) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า พนักงาน ผู้จัดจำหน่าย ประเภทสินค้า โปรโมชั่น ตลอดจนข้อมูลการสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า โดย Dataset หลักประกอบด้วย 12 ตาราง จำนวนรวม 1,631,380 Records และ 39 Columns

จากการศึกษาลักษณะและโครงสร้างของข้อมูล พบว่า Dataset มีความสอดคล้องกับระบบ OLTP เนื่องจากมีทั้ง ข้อมูลหลัก (Master Data) และ ข้อมูลธุรกรรม (Transaction Data) ซึ่งทำงานเชื่อมโยงกันเพื่อรองรับกระบวนการขายสินค้า

3.1 ข้อมูลหลัก (Master Data)

ข้อมูลหลักเป็นข้อมูลที่ใช้ประกอบการทำธุรกรรมและไม่ได้เกิดขึ้นใหม่ทุกครั้งที่มีการซื้อสินค้า ประกอบด้วยตารางต่าง ๆ ดังนี้

## รายละเอียดตารางข้อมูลหลัก

| ตาราง | รายละเอียด | ตัวอย่างข้อมูล | จำนวน Records |
|:---:|:---|:---|---:|
| `customers` | ใช้จัดเก็บข้อมูลลูกค้า | `customer_id`, `city`, `signup_date` | 50,000 |
| `products` | ใช้จัดเก็บข้อมูลสินค้า | `product_id`, `category_id`, `supplier_id`, `price` | 10,000 |
| `categories` | ใช้จัดเก็บข้อมูลประเภทสินค้า | `category_id`, `category_name` | 30 |
| `suppliers` | ใช้จัดเก็บข้อมูลผู้จัดจำหน่าย | `supplier_id`, `supplier_name` | 200 |
| `stores` | ใช้จัดเก็บข้อมูลสาขา | `store_id`, `store_name` | 100 |
| `employees` | ใช้จัดเก็บข้อมูลพนักงาน | `employee_id`, `employee_name`, `store_id` | 1,000 |
| `promotions` | ใช้จัดเก็บข้อมูลโปรโมชั่น | `promotion_id`, `promotion_name` | 50 |

ข้อมูลเหล่านี้จะถูกนำมาใช้ประกอบการทำธุรกรรม เช่น เมื่อมีการสั่งซื้อสินค้า ระบบจะนำข้อมูลลูกค้า สินค้า สาขา และโปรโมชั่นที่เกี่ยวข้องมาเชื่อมโยงกับคำสั่งซื้อ

3.2 ข้อมูลธุรกรรม (Transaction Data)

ข้อมูลธุรกรรมเป็นข้อมูลที่เกิดขึ้นจากกิจกรรมต่าง ๆ ของระบบ โดยมีการเพิ่มข้อมูลเมื่อเกิดเหตุการณ์ใหม่ เช่น การสั่งซื้อ การชำระเงิน หรือการจัดส่ง ประกอบด้วย

## รายละเอียดตารางข้อมูล

| ตาราง | รายละเอียด | ตัวอย่างข้อมูล | จำนวน Records |
|:---:|:---|:---|---:|
| `customers` | ใช้จัดเก็บข้อมูลลูกค้า | `customer_id`, `city`, `signup_date` | 50,000 |
| `products` | ใช้จัดเก็บข้อมูลสินค้า | `product_id`, `category_id`, `supplier_id`, `price` | 10,000 |
| `categories` | ใช้จัดเก็บข้อมูลประเภทสินค้า | `category_id`, `category_name` | 30 |
| `suppliers` | ใช้จัดเก็บข้อมูลผู้จัดจำหน่าย | `supplier_id`, `supplier_name` | 200 |
| `stores` | ใช้จัดเก็บข้อมูลสาขา | `store_id`, `store_name` | 100 |
| `employees` | ใช้จัดเก็บข้อมูลพนักงาน | `employee_id`, `employee_name`, `store_id` | 1,000 |
| `promotions` | ใช้จัดเก็บข้อมูลโปรโมชั่น | `promotion_id`, `promotion_name` | 50 |
| `orders` | ใช้บันทึกข้อมูลคำสั่งซื้อ | `order_id`, `customer_id`, `store_id`, `order_date`, `promotion_id` | 300,000 |
| `order_items` | ใช้บันทึกรายละเอียดสินค้าในแต่ละคำสั่งซื้อ | `order_item_id`, `order_id`, `product_id`, `qty`, `price` | 600,000 |
| `payments` | ใช้บันทึกข้อมูลการชำระเงิน | `payment_id`, `order_id`, `amount` | 300,000 |
| `shipments` | ใช้บันทึกข้อมูลการจัดส่ง | `shipment_id`, `order_id`, `status` | 300,000 |
| `returns` | ใช้บันทึกข้อมูลการคืนสินค้า | `return_id`, `order_item_id`, `refund` | 30,000 |
ตารางเหล่านี้มีความสำคัญต่อระบบ OLTP เนื่องจากเป็นข้อมูลที่เกิดขึ้นจากธุรกรรมโดยตรงและมีการบันทึกข้อมูลเป็นรายรายการ

3.3 กระบวนการทำงานของ OLTP ใน Dataset

การทำงานของระบบสามารถอธิบายเป็นกระบวนการตั้งแต่ลูกค้าทำการสั่งซื้อจนถึงการจัดส่งสินค้าได้ดังนี้

ขั้นตอนที่ 1 ลูกค้า

ลูกค้าถูกจัดเก็บในตาราง customers โดยมี customer_id เป็นรหัสสำหรับระบุลูกค้าแต่ละราย

↓

ขั้นตอนที่ 2 การสั่งซื้อสินค้า

เมื่อลูกค้าทำการสั่งซื้อ ระบบจะสร้างข้อมูลในตาราง orders โดยกำหนด order_id เพื่อระบุคำสั่งซื้อแต่ละรายการ และเชื่อมโยงกับ customer_id เพื่อระบุว่าคำสั่งซื้อเป็นของลูกค้ารายใด

↓

ขั้นตอนที่ 3 การบันทึกรายการสินค้า

รายละเอียดสินค้าที่อยู่ภายในคำสั่งซื้อจะถูกบันทึกใน order_items โดยใช้ order_id เชื่อมโยงกับคำสั่งซื้อ และใช้ product_id เชื่อมโยงกับข้อมูลสินค้าใน products

↓

ขั้นตอนที่ 4 การชำระเงิน

เมื่อมีการชำระเงิน ระบบจะบันทึกข้อมูลลงใน payments โดยใช้ order_id เพื่อระบุว่าการชำระเงินนั้นเกี่ยวข้องกับคำสั่งซื้อใด

↓

ขั้นตอนที่ 5 การจัดส่ง

เมื่อดำเนินการจัดส่ง ระบบจะสร้างข้อมูลใน shipments และใช้ status เพื่อระบุสถานะของการจัดส่ง

↓

ขั้นตอนที่ 6 การคืนสินค้า

หากลูกค้าต้องการคืนสินค้า ระบบจะบันทึกข้อมูลใน returns และใช้ order_item_id เพื่อระบุว่าสินค้าที่คืนเป็นรายการใดในคำสั่งซื้อ
ดังนั้น กระบวนการโดยรวมสามารถแสดงได้ดังนี้

Customer → Order → Order Item → Payment → Shipment → Return

3.4 ความสัมพันธ์ของข้อมูลที่สนับสนุนการทำงานแบบ OLTP

อีกหนึ่งลักษณะสำคัญของ Dataset คือการมีการเชื่อมโยงข้อมูลระหว่างตารางผ่านรหัสประจำข้อมูล เช่น

customer_id เชื่อมโยงข้อมูลลูกค้ากับคำสั่งซื้อ
order_id เชื่อมโยงคำสั่งซื้อกับรายละเอียดสินค้า การชำระเงิน และการจัดส่ง
product_id เชื่อมโยงรายการสินค้าเข้ากับข้อมูลสินค้า
category_id เชื่อมโยงสินค้าเข้ากับประเภทสินค้า
supplier_id เชื่อมโยงสินค้าเข้ากับผู้จัดจำหน่าย
store_id เชื่อมโยงคำสั่งซื้อและพนักงานกับสาขา
promotion_id เชื่อมโยงคำสั่งซื้อกับโปรโมชั่น
order_item_id เชื่อมโยงรายการสินค้าเข้ากับข้อมูลการคืนสินค้า

การแบ่งข้อมูลออกเป็นหลายตารางและเชื่อมโยงกันดังกล่าวช่วยลดการจัดเก็บข้อมูลซ้ำซ้อน และทำให้สามารถจัดการข้อมูลแต่ละส่วนได้อย่างเป็นระบบ

3.5 เหตุผลที่ Dataset มีลักษณะเป็น OLTP

จากการตรวจสอบ Dataset สามารถระบุเหตุผลที่สนับสนุนว่า Dataset นี้มีลักษณะเป็น OLTP ได้ดังนี้

ประการที่หนึ่ง Dataset มีตารางที่ใช้บันทึกธุรกรรมโดยตรง เช่น orders, order_items, payments, shipments และ returns

ประการที่สอง มีตารางข้อมูลหลัก เช่น customers, products, stores, categories, suppliers, employees และ promotions ซึ่งทำหน้าที่สนับสนุนการทำธุรกรรม

ประการที่สาม ข้อมูลมีรายละเอียดในระดับรายการธุรกรรม เช่น order_items สามารถระบุได้ว่าคำสั่งซื้อหนึ่งรายการประกอบด้วยสินค้าอะไร จำนวนเท่าใด และราคาเท่าใด

ประการที่สี่ Dataset มีจำนวนข้อมูลค่อนข้างมาก โดยมีข้อมูลรวม 1,631,380 Records ซึ่งส่วนใหญ่เป็นข้อมูลธุรกรรม เช่น order_items จำนวน 600,000 Records และ orders, payments และ shipments ตารางละ 300,000 Records

ประการที่ห้า ตารางต่าง ๆ มีการเชื่อมโยงข้อมูลด้วยรหัส เช่น order_id, customer_id และ product_id ซึ่งเป็นลักษณะสำคัญของฐานข้อมูลที่ใช้จัดการธุรกรรม

ประการที่หก โครงสร้างของ Dataset สามารถสะท้อนกระบวนการดำเนินงานของธุรกิจค้าปลีกตั้งแต่การสั่งซื้อ การบันทึกรายการสินค้า การชำระเงิน การจัดส่ง และการคืนสินค้า

3.6 สรุปการวิเคราะห์ OLTP

จากการวิเคราะห์ Dataset พบว่า Dataset มีลักษณะสอดคล้องกับ OLTP (Online Transaction Processing) เนื่องจากเป็นข้อมูลที่ใช้สนับสนุนกระบวนการดำเนินงานของธุรกิจค้าปลีก โดยมีทั้งข้อมูลหลักและข้อมูลธุรกรรมที่มีการเชื่อมโยงกันอย่างเป็นระบบ

ข้อมูลธุรกรรมที่สำคัญ ได้แก่ orders, order_items, payments, shipments และ returns ซึ่งทำหน้าที่บันทึกเหตุการณ์ต่าง ๆ ที่เกิดขึ้นจากการดำเนินงาน ขณะที่ customers, products, categories, suppliers, stores, employees และ promotions ทำหน้าที่เป็นข้อมูลหลักที่ใช้ประกอบการทำธุรกรรม

นอกจากนี้ Dataset ยังมีการเชื่อมโยงข้อมูลผ่านรหัสต่าง ๆ เช่น customer_id, order_id, product_id และ store_id ทำให้สามารถติดตามข้อมูลของธุรกรรมตั้งแต่การสั่งซื้อจนถึงการชำระเงิน การจัดส่ง และการคืนสินค้าได้

ดังนั้น Dataset นี้สามารถจัดอยู่ในลักษณะของฐานข้อมูล OLTP สำหรับระบบค้าปลีก เนื่องจากมีโครงสร้างที่มุ่งเน้นการจัดเก็บข้อมูลธุรกรรมที่เกิดขึ้นในแต่ละวัน มีข้อมูลในระดับรายละเอียดของ Transaction และมีความสัมพันธ์ระหว่างข้อมูลหลายตารางเพื่อสนับสนุนกระบวนการทำงานของระบบค้าปลีกอย่างเป็นระบบและมีประสิทธิภาพ



## ER Diagram (หลิน)
<img src="./readme_images/Miniproject Diagram.drawio (1).png">
## Database Relationships

| Table | Relationship | Table |
|---|:---:|---|
| categories | 1:N | products |
| suppliers | 1:N | products |
| products | 1:N | order_items |
| orders | 1:N | order_items |
| order_items | 1:N | returns |
| customers | 1:N | orders |
| stores | 1:N | orders |
| promotions | 1:N | orders |
| orders | 1:N | payments |
| orders | 1:N | shipments |
| stores | 1:N | employees |

## Business Questions (ฟีฟ่า)

<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0001" src="https://github.com/user-attachments/assets/9e722ba4-a7f5-4f9a-b15c-2656578d17d0" />
<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0002" src="https://github.com/user-attachments/assets/82c15f58-89e1-46f5-8bcd-47866d7e536e" />
<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0003" src="https://github.com/user-attachments/assets/0afbc732-5f5c-4ae6-8092-93bda6e92caf" />


## Multidimensional Data Model Design (ต้นข้าว)
เริ่มจากการวิเคราะห์ข้อมูลจากระบบขายปลีกที่ประกอบด้วยไฟล์ข้อมูล 12 ตาราง ได้แก่ Categories, Customers, Employees, Order Items, Orders, Payments, Products, Promotions, Returns, Shipments, Stores และ Suppliers
จากนั้นกำหนด Business Process หลัก คือ กระบวนการขายสินค้า (Sales Process) เนื่องจากเป็นกระบวนการที่เชื่อมโยงข้อมูลส่วนใหญ่ของระบบ เช่น ลูกค้า สินค้า ร้านค้า พนักงาน โปรโมชั่น การชำระเงิน และการจัดส่งสินค้า
จากนั้นแยกข้อมูลเชิงพรรณนาออกเป็น Dimension Tables และเก็บข้อมูลเชิงตัวเลขที่ใช้วิเคราะห์ไว้ใน Fact Table
- Dim_Date: Day → Month → Quarter → Year
ใช้ในการดูยอดขายแต่ละวัน เดือน ไตรมาส และปี
- Dim_Product: Category → Sub-Category
ใช้ในการจัดหมวดหมู่ผลิตภัณฑ์
- Dim_Customer: Customer
ใช้ในการวิเคราะห์พฤติกรรมของลูกค้า
- Dim_Store: Store → District → Province → Region
ใช้ในการวิเคราะห์ผลการดำเนินงานรายสาขาและพื้นที่
- Dim_Employee: Employee
ใช้ในการวิเคราะห์พฤติกรรมการทำงานของพนักงาน
- Dim_Promotion: Promotion => Discount, Special Deal, Cupon, Point
ใช้ในการวิเคราะห์ส่วนของโปรโมชั่น เช่น ส่วนลด ของแถม ดีล คูปอง และ พอยท์
- Dim_Supplier: Supplier
ใช้ในการวิเคราะห์เรื่องซัพพลายเออร์,การจัดการทรัพยากร
- Dim_Payment: Payment Method ใช้ในการวิเคราห์วิธีการชำระเงินของลูกค้า

ในส่วนของ Fact Tables [Fact_Sales] จะมี Source หลักๆ คือ
- Order_items.csv
- Orders.csv

ในส่วนไฟล์ข้อมูล Returns และ Shipments สามารถนำมาสร้างเป็น Fact แยกออกมา
- Returns  → Fact_Returns เพื่อวิเคราะห์อัตราการคืนสินค้า (Return Rate) ตามสาขา หรือตามประเภทสินค้า
- Shipments  →  Fact_Shipments เพื่อวัดประสิทธิภาพระยะเวลาจัดส่ง (Delivery Lead Time) และคลังสินค้า

กำหนด Grain ของ Fact Table ว่า
	“1 แถว แทนสินค้า 1 รายการในคำสั่งซื้อ 1 รายการ (One Order Line Item)”

Foreign Keys:
- Date_ID
- Product_ID
- Customer_ID
- Store_ID
- Employee_ID
- Promotion_ID
- Supplier_ID
- Payment_ID

Measure
- Quantity (จำนวนสินค้า) จำนวนชิ้นที่ขายได้ในรายการนั้น
- Sales Amount (ยอดขาย) จำนวนเงินรวมหลังหักส่วนลด หรือราคาสุทธิ
- Discount (ส่วนลด) มูลค่าส่วนลดที่ให้ในรายการนั้น
- Profit (กำไรสุทธิ) กำไรสุทธิจากรายการนั้น
- Calculated MeasuresProfit Margin (%):
  - ("Profit" /"Sales Amount" )×100
  - Average Selling Price (ราคาขายเฉลี่ยต่อชิ้น): "Sales Amount"/"Quantity" 

## Data Model Diagram (Star Scheme) แซนด์วิช
<img src="./readme_images/star schema.jpg">

## การดำเนินงานด้านการจัดการข้อมูลด้วยกระบวนการ ELT

1. กระบวนการ ELT (ELT Process)
## 1.1 หลักการและแนวคิดของ ELT

โครงงานนี้ใช้กระบวนการ ELT (Extract, Load, Transform) ในการจัดการข้อมูล โดยมีวัตถุประสงค์เพื่อรวบรวมข้อมูลจากระบบต้นทาง จัดเก็บข้อมูลในฐานข้อมูล และดำเนินการทำความสะอาดและแปลงข้อมูลภายหลังจากที่ข้อมูลถูก Load เข้าสู่ฐานข้อมูลแล้ว

ELT ประกอบด้วย 3 ขั้นตอนหลัก ได้แก่

Extract – การดึงข้อมูลจากแหล่งข้อมูลต้นทาง
Load – การนำข้อมูลเข้าสู่ฐานข้อมูลในรูปแบบ Raw/Staging
Transform – การทำความสะอาด แปลง และจัดโครงสร้างข้อมูลเพื่อเตรียมเข้าสู่ Data Warehouse

| ขั้นตอน (Stage) | ชื่อชั้นข้อมูล (Layer Name) | เครื่องมือ / เทคโนโลยี (Tools) | หน้าที่และการทำงาน (Function / Tasks) |
| :--- | :--- | :--- | :--- |
| **1. Source** | **แหล่งข้อมูลต้นทาง** | Google Drive / CSV Files | จัดเก็บไฟล์ข้อมูลดิบรูปแบบ CSV บน Google Drive พร้อมสำหรับการดึงไปใช้งาน |
| **2. Extract** | **Raw / Staging** | DuckDB | ทำการดึงข้อมูลดิบ (Extract) เข้าสู่พื้นที่พักข้อมูล (Staging Area) เพื่อเตรียมนำไปแปลงสภาพ |
| **3. Transform** | **Transform Layer** | Data Processing Engine | ทำการทำความสะอาดข้อมูล (Cleaning), เชื่อมโยงข้อมูล (Join), แปลงชนิดข้อมูล (Type Conversion) และคำนวณค่าต่างๆ (Calculation) |
| **4. Storage** | **Data Warehouse** | Relational / Analytical DB | จัดเก็บข้อมูลที่ผ่านการแปลงแล้วลงในรูปแบบ **Fact Tables** (ตารางข้อเท็จจริง) และ **Dimension Tables** (ตารางมิติ) |
| **5. Output** | **Analysis** | BI Tools / Dashboards / SQL | นำข้อมูลที่จัดเก็บใน Data Warehouse ไปวิเคราะห์ ทำรายงาน หรือนำเสนอต่อผู้ใช้งาน |

## 1.2 โครงสร้าง Dataset

Dataset ที่ใช้ในโครงงานเป็นข้อมูลระบบค้าปลีก ประกอบด้วยข้อมูลเกี่ยวกับลูกค้า สินค้า ร้านค้า คำสั่งซื้อ การชำระเงิน การจัดส่ง การคืนสินค้า โปรโมชั่น และข้อมูลที่เกี่ยวข้องกับการดำเนินงานของธุรกิจค้าปลีก

จากการตรวจสอบข้อมูลพบ 12 ตารางหลัก ดังนี้
นอกจากนี้ยังพบไฟล์ข้อมูลประเภท TXT และ ZIP ซึ่งเป็นข้อมูลตัวอย่างขนาดเล็ก จึงแยกออกจาก Dataset หลักเพื่อให้การวิเคราะห์โครงสร้างฐานข้อมูลค้าปลีกมีความชัดเจน

| ลำดับ | ตาราง | Records | Columns | ประเภทข้อมูล |
| :---: | :--- | :---: | :---: | :---: |
| 1 | employees | 1,000 | 3 | Master |
| 2 | returns | 30,000 | 3 | Transaction |
| 3 | products | 10,000 | 4 | Master |
| 4 | suppliers | 200 | 2 | Master |
| 5 | categories | 30 | 2 | Master |
| 6 | promotions | 50 | 2 | Master |
| 7 | stores | 100 | 2 | Master |
| 8 | customers | 50,000 | 3 | Master |
| 9 | payments | 300,000 | 3 | Transaction |
| 10 | orders | 300,000 | 5 | Transaction |
| 11 | order_items | 600,000 | 5 | Transaction |
| 12 | shipments | 300,000 | 3 | Transaction |

รวมข้อมูลทั้งหมด
<1,631,380 Records และ 39 Columns>

## 1.3 การเตรียมสภาพแวดล้อมสำหรับ ELT

การดำเนินงานใช้ Google Colab เป็นสภาพแวดล้อมสำหรับเขียนและประมวลผล Python โดยข้อมูลต้นทางถูกจัดเก็บอยู่ใน Google Drive

เครื่องมือที่ใช้ ได้แก่  Google Drive ,Google Colab,Python ,Pandas, DuckDB ,SQL


1.3.1 ติดตั้ง Library
!pip install duckdb -q

import pandas as pd
import duckdb
import os

1.3.2 เชื่อมต่อ Google Drive
from google.colab import drive

drive.mount('/content/drive')

1.3.3 กำหนด Path ของ Dataset
path = '/content/drive/My Drive/miniproject_สินค้าปลีก'

print("Dataset Path:")
print(path)

print("\nFiles:")
print(os.listdir(path))

1.4 Extract
1.4.1 ความหมายของ Extract

Extract คือขั้นตอนการดึงข้อมูลจากระบบต้นทางเข้าสู่กระบวนการประมวลผล

ในโครงงานนี้ แหล่งข้อมูลต้นทางคือไฟล์ CSV ที่อยู่ใน Google Drive โดยมีทั้งหมด 12 ตารางหลัก ได้แก่

| ลำดับ | ชื่อไฟล์ (File Name) |
| :---: | :--- |
| 1 | employees.csv |
| 2 | returns.csv |
| 3 | products.csv |
| 4 | suppliers.csv |
| 5 | categories.csv |
| 6 | promotions.csv |
| 7 | stores.csv |
| 8 | customers.csv |
| 9 | payments.csv |
| 10 | orders.csv |
| 11 | order_items.csv |
| 12 | shipments.csv |

1.4.2 กำหนดรายชื่อตาราง
tables = [
    'employees',
    'returns',
    'products',
    'suppliers',
    'categories',
    'promotions',
    'stores',
    'customers',
    'payments',
    'orders',
    'order_items',
    'shipments'
]

print("จำนวนตารางทั้งหมด:", len(tables))

1.4.3 อ่านข้อมูล CSV

loaded_data = {}

for table in tables:
    file_path = os.path.join(path, table + '.csv')
    df = pd.read_csv(file_path)
    loaded_data[table] = df
    print(f"{table}.csv -> {len(df):,} records")


1.4.4 ตรวจสอบผลการ Extract

for table in tables:
    df = loaded_data[table]
    print(
        f"{table:15} | "
        f"Rows = {len(df):,} | "
        f"Columns = {len(df.columns)}"
    )

## 1.5 Load
1.5.1 ความหมายของ Load

หลังจาก Extract ข้อมูลจาก CSV แล้ว ขั้นตอนต่อไปคือ Load

ในโครงงานนี้ข้อมูลจะถูกนำเข้าสู่ DuckDB โดยจัดเก็บในรูปแบบ Staging Tables

1.5.2 สร้าง DuckDB

db_path = os.path.join(path, 'retail.duckdb')
con = duckdb.connect(db_path)

print("เชื่อมต่อ DuckDB สำเร็จ")
print("Database:", db_path)

1.5.3 Load CSV → Staging Tables

for table in tables:
    file_path = os.path.join(path, table + '.csv')

    con.execute(f"""
        CREATE OR REPLACE TABLE stg_{table} AS
        SELECT *
        FROM read_csv_auto(?)
    """, [file_path])

    print(f"Loaded: {table}.csv -> stg_{table}")

	1.5.4 ทำไมต้องใช้ Staging Layer?

Staging Layer มีหน้าที่เป็นพื้นที่พักข้อมูลก่อน Transform
### ข้อดีของการใช้ Raw / Staging Layer (DuckDB)

| ลำดับ | รายการข้อดี | รายละเอียดการทำงาน |
| :---: | :--- | :--- |
| 1 | **Data Persistence** | เก็บข้อมูลจาก Source ไว้ใน Database โดยตรง |
| 2 | **Performance Optimization** | ลดการอ่านไฟล์ CSV ซ้ำหลายครั้ง ช่วยประหยัดเวลาการทำงาน |
| 3 | **Data Validation** | ตรวจสอบข้อมูลเบื้องต้นก่อนเข้าสู่กระบวนการ Transform |
| 4 | **Record Counting** | สามารถตรวจสอบจำนวน Records ทั้งหมดได้อย่างแม่นยำ |
| 5 | **Data Type Inspection** | ตรวจสอบชนิดของข้อมูล (Data Type) ในแต่ละคอลัมน์ได้ |
| 6 | **Missing Value Check** | ตรวจสอบข้อมูลสูญหายหรือค่าว่าง (Null / Missing Value) |
| 7 | **Duplicate Identification** | ตรวจสอบและค้นหาข้อมูลที่ซ้ำซ้อน (Duplicate Data) |
| 8 | **Architecture Separation** | แยกข้อมูลดิบต้นทาง (Source) ออกจากข้อมูลที่แปลงแล้ว (Transformed Data) อย่างเป็นระบบ |

1.5.5 ตรวจสอบว่า Load สำเร็จหรือไม่

tables_in_db = con.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main'
    ORDER BY table_name
""").df()

display(tables_in_db)

1.5.6 ตรวจสอบจำนวน Records หลัง Load

load_result = []

for table in tables:
    count = con.execute(
        f"SELECT COUNT(*) FROM stg_{table}"
    ).fetchone()[0]

    load_result.append({
        'Source File': table + '.csv',
        'Staging Table': 'stg_' + table,
        'Records': count
    })

load_summary = pd.DataFrame(load_result)

display(load_summary)

1.5.7 ตรวจสอบจำนวน Records รวม

total_records = load_summary['Records'].sum()

print(f"จำนวนตารางทั้งหมด : {len(load_summary)} ตาราง")
print(f"จำนวน Records รวม : {total_records:,} Records")


## 1.6 Transform

หลังจากข้อมูลถูก Load เข้าสู่ Staging Layer แล้ว จะเข้าสู่ขั้นตอน Transform

Transform เป็นส่วนสำคัญของ ELT เนื่องจากเป็นขั้นตอนที่ทำให้ข้อมูลพร้อมสำหรับ Data Warehouse และการวิเคราะห์

กระบวนการ Transform ประกอบด้วย

### 1.6 Transform Layer

หลังจากข้อมูลถูก Load เข้าสู่ Staging Layer แล้ว จะเข้าสู่ขั้นตอน **Transform** ซึ่งเป็นส่วนสำคัญของสถาปัตยกรรม **ELT (Extract, Load, Transform)** เนื่องจากเป็นขั้นตอนการแปลงสภาพข้อมูลให้อยู่ในรูปแบบที่สมบูรณ์ ถูกต้อง และพร้อมสำหรับการนำไปจัดเก็บใน **Data Warehouse** เพื่อการวิเคราะห์ต่อไป

---

**กระบวนการ Transform ประกอบด้วย:**

| ลำดับ | กระบวนการ (Process) | รายละเอียดการทำงาน (Description) |
| :---: | :--- | :--- |
| **1** | **Data Cleaning** | การทำความสะอาดข้อมูล จัดการค่าที่หายไป (Null / Missing values), ลบข้อมูลซ้ำซ้อน (Duplicates) และแก้ไขค่าที่ไม่ถูกต้อง |
| **2** | **Data Type Conversion** | การแปลงชนิดข้อมูลให้ถูกต้องและเหมาะสมกับการจัดเก็บ เช่น แปลง ข้อความ (String) เป็น วันที่ (Date/Timestamp) หรือ ตัวเลข (Numeric) |
| **3** | **Data Transformation & Standardisation** | การปรับรูปแบบข้อมูลให้อยู่ในมาตรฐานเดียวกัน เช่น ตัดข้อความส่วนเกิน (Trim whitespace) หรือปรับรูปแบบตัวพิมพ์เล็ก-ใหญ่ (Upper/Lower case) |
| **4** | **Calculations & Business Logic** | การคำนวณตัวเลขและสร้างคอลัมน์ใหม่ตามเงื่อนไขทางธุรกิจ เช่น ยอดขายรวม (Total Price), ส่วนลด (Discount) หรือกำไรขั้นต้น (Margin) |
| **5** | **Data Joining & Structuring** | การเชื่อมโยงตารางข้อมูล (JOIN) และจัดกลุ่มโครงสร้างเพื่อเตรียมแปลงเป็น **Dim / Fact Tables** สำหรับ Data Warehouse |

1.6.1 Data Cleaning
ตรวจสอบ Missing Value

for table in tables:
    df = con.execute(
        f"SELECT * FROM stg_{table}"
    ).df()

    missing = df.isnull().sum()

    print("=" * 60)
    print(f"Missing Value: {table}")
    print(missing)

